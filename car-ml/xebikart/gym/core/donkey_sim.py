# Original author: Tawn Kramer

import asyncore
import base64
import time
from io import BytesIO
from threading import Thread

import numpy as np
from PIL import Image

from xebikart.gym.core.fps import FPSTimer
from xebikart.gym.core.tcp_server import IMesgHandler, SimServer


class DonkeyUnitySimController:
    """
    Wrapper for communicating with unity simulation.

    :param level: (int) Level index
    :param port: (int) Port to use for communicating with the simulator
    """

    def __init__(self, level, port=9090, camera_shape=(120, 160, 3)):
        self.level = level
        self.verbose = False

        # sensor size - height, width, depth
        self.camera_img_size = camera_shape

        self.address = ('0.0.0.0', port)

        # Socket message handler
        self.handler = DonkeyUnitySimHandler(level, self.camera_img_size)
        # Create the server to which the unity sim will connect
        self.server = SimServer(self.address, self.handler)
        # Start the Asynchronous socket handler thread
        self.thread = Thread(target=asyncore.loop)
        self.thread.daemon = True
        self.thread.start()

    def close_connection(self):
        self.server.handle_close()
        self.thread.join()

    def wait_until_loaded(self):
        """
        Wait for a client (Unity simulator).
        """
        while not self.handler.loaded:
            print("Waiting for sim to start..."
                  "if the simulation is running, press EXIT to go back to the menu")
            time.sleep(3.0)

    def reset(self):
        self.handler.reset()

    def get_sensor_size(self):
        """
        :return: (int, int, int)
        """
        return self.handler.get_sensor_size()

    def take_action(self, action):
        self.handler.take_action(action)

    def observe(self):
        """
        :return: (np.ndarray)
        """
        return self.handler.observe()

    def quit(self):
        pass

    def render(self, mode):
        pass

    def has_hit(self):
        return self.handler.hit != "none"

    def cte(self):
        return self.handler.cte

    def last_throttle(self):
        return self.handler.last_throttle

    def info(self):
        return {
            "x": self.handler.x,
            "y": self.handler.y,
            "z": self.handler.z,
            "speed": self.handler.speed,
            "cte": self.handler.cte,
            "hit": self.handler.hit != "none",
            "throttle": self.handler.last_throttle,
            "steering": self.handler.steering_angle
        }


class DonkeyUnitySimHandler(IMesgHandler):
    """
    Socket message handler.

    :param level: (int) Level ID
    """

    def __init__(self, level, camera_shape):
        self.level_idx = level
        self.sock = None
        self.loaded = False
        self.verbose = False
        self.timer = FPSTimer(verbose=0)

        # sensor size - height, width, depth
        self.camera_img_size = camera_shape
        self.image_array = np.zeros(self.camera_img_size)
        self.original_image = None
        self.last_obs = None
        self.last_throttle = 0.0
        # Disabled: hit was used to end episode when bumping into an object
        self.hit = "none"
        # Cross track error
        self.cte = 0.0
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.steering_angle = 0.0
        self.current_step = 0
        self.speed = 0
        self.steering = None

        # Define which method should be called
        # for each type of message
        self.fns = {'telemetry': self.on_telemetry,
                    "scene_selection_ready": self.on_scene_selection_ready,
                    "scene_names": self.on_recv_scene_names,
                    "car_loaded": self.on_car_loaded}

    def on_connect(self, socket_handler):
        """
        :param socket_handler: (socket object)
        """
        self.sock = socket_handler

    def on_disconnect(self):
        """
        Close socket.
        """
        self.sock.close()
        self.sock = None

    def on_recv_message(self, message):
        """
        Distribute the received message to the appropriate function.

        :param message: (dict)
        """
        if 'msg_type' not in message:
            print('Expected msg_type field')
            return

        msg_type = message['msg_type']
        if msg_type in self.fns:
            self.fns[msg_type](message)
        else:
            print('Unknown message type', msg_type)

    def reset(self):
        """
        Global reset, notably it
        resets car to initial position.
        """
        if self.verbose:
            print("resetting")
        self.image_array = np.zeros(self.camera_img_size)
        self.last_obs = None
        self.hit = "none"
        self.cte = 0.0
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.current_step = 0
        self.send_reset_car()
        self.send_control(0, 0)
        time.sleep(1.0)
        self.timer.reset()

    def get_sensor_size(self):
        """
        :return: (tuple)
        """
        return self.camera_img_size

    def take_action(self, action):
        """
        :param action: ([float]) Steering and throttle
        """
        if self.verbose:
            print("take_action")

        throttle = action[1]
        self.steering = action[0]
        self.last_throttle = throttle
        self.current_step += 1

        self.send_control(self.steering, throttle)

    def observe(self):
        while self.last_obs is self.image_array:
            time.sleep(1.0 / 120.0)

        self.last_obs = self.image_array
        observation = self.image_array

        self.timer.on_frame()

        return observation

    # ------ Socket interface ----------- #

    def on_telemetry(self, data):
        """
        Update car info when receiving telemetry message.

        :param data: (dict)
        """
        img_string = data["image"]
        image = Image.open(BytesIO(base64.b64decode(img_string)))
        # Resize and crop image
        image = np.array(image)
        # Save original image for render
        self.original_image = np.copy(image)
        # Resize if using higher resolution images
        # image = cv2.resize(image, CAMERA_RESOLUTION)
        # Convert RGB to BGR
        image = image[:, :, ::-1]
        self.image_array = image
        # Here resize is not useful for now (the image have already the right dimension)
        # self.image_array = cv2.resize(image, (IMAGE_WIDTH, IMAGE_HEIGHT))

        # name of object we just hit. "none" if nothing.
        # NOTE: obstacle detection disabled
        # if self.hit == "none":
        #     self.hit = data["hit"]

        self.x = data["pos_x"]
        self.y = data["pos_y"]
        self.z = data["pos_z"]
        self.steering_angle = data['steering_angle']
        self.speed = data["speed"]

        # Cross track error not always present.
        # Will be missing if path is not setup in the given scene.
        # It should be setup in the 3 scenes available now.
        try:
            self.cte = data["cte"]
            # print(self.cte)
        except KeyError:
            print("No Cross Track Error in telemetry")
            pass

    def on_scene_selection_ready(self, _data):
        """
        Get the level names when the scene selection screen is ready
        """
        print("Scene Selection Ready")
        self.send_get_scene_names()

    def on_car_loaded(self, _data):
        if self.verbose:
            print("Car Loaded")
        self.loaded = True

    def on_recv_scene_names(self, data):
        """
        Select the level.

        :param data: (dict)
        """
        if data is not None:
            names = data['scene_names']
            if self.verbose:
                print("SceneNames:", names)
            self.send_load_scene(names[self.level_idx])

    def send_control(self, steer, throttle):
        """
        Send message to the server for controlling the car.

        :param steer: (float)
        :param throttle: (float)
        """
        if not self.loaded:
            return
        msg = {'msg_type': 'control', 'steering': steer.__str__(), 'throttle': throttle.__str__(), 'brake': '0.0'}
        self.queue_message(msg)

    def send_reset_car(self):
        """
        Reset car to initial position.
        """
        msg = {'msg_type': 'reset_car'}
        self.queue_message(msg)

    def send_get_scene_names(self):
        """
        Get the different levels availables
        """
        msg = {'msg_type': 'get_scene_names'}
        self.queue_message(msg)

    def send_load_scene(self, scene_name):
        """
        Load a level.

        :param scene_name: (str)
        """
        msg = {'msg_type': 'load_scene', 'scene_name': scene_name}
        self.queue_message(msg)

    def send_exit_scene(self):
        """
        Go back to scene selection.
        """
        msg = {'msg_type': 'exit_scene'}
        self.queue_message(msg)

    def queue_message(self, msg):
        """
        Add message to socket queue.

        :param msg: (dict)
        """
        if self.sock is None:
            if self.verbose:
                print('skipping:', msg)
            return

        if self.verbose:
            print('sending', msg)
        self.sock.queue_message(msg)
