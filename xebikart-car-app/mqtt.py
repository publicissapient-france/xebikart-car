import json
import time
import paho.mqtt.client as mqtt

import config


def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))


def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.payload))


def on_publish(mqttc, obj, result):
    print("mid: " + str(result))
    pass


class MQTTClient:

    def __init__(self, publish_delay=1):
        self.publish_delay = publish_delay

        self.json_encoder = json.JSONEncoder()

        self.client = mqtt.Client()
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.on_publish = on_publish

        username = config.RABBITMQ_USERNAME
        password = config.RABBITMQ_PASSWORD

        host = config.RABBITMQ_HOST
        port = config.RABBITMQ_PORT

        self.topic = config.RABBITMQ_TOPIC

        self.client.username_pw_set(username=username, password=password)
        self.client.connect(host, port, 60)

        self.running = True
        self.output_payload = None

        print("MQTT client initialized")

    def update(self):
        while self.running:
            if self.output_payload is not None:
                self.client.publish(self.topic, json.dumps(self.output_payload))
                time.sleep(self.publish_delay)

    def run_threaded(
            self,
            mode,
            user_angle, user_throttle,  # from controller
            x, y, z, angle,  # from lidar
            dx, dy, dz, tx, ty, tz  # from imu
    ):
        self.output_payload = {
            'car': config.CAR_ID,
            'mode': mode,
            'user': {
                "angle": user_angle,
                "throttle": user_throttle
            },
            'position': {
                'x': x,
                'y': y,
                'z': z
            },
            'angle': angle,
            'acceleration': {
                'x': dx,
                'y': dy,
                'z': dz
            },
            'angular_speed': {
                'x': tx,
                'y': ty,
                'z': tz
            }
        }
        return 0

    def shutdown(self):
        self.running = False
        self.client.disconnect()
        self.client.loop_stop()
