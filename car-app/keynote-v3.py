#!/usr/bin/env python3

"""
Usage:
    keynote-v3.py --steering-model=<steering_model_path> --exit-model=<exit_model_path> [--color=<color>] [--throttle=<throttle>]

Options:
    -h --help                    Show this screen.
    --steering-model=<path>      Path to h5 model (steering only) (.h5)
    --exit-model=<path>          Path to tflite model (exit) (.tflite)
    --color=<color>              Color to detect in picture [default: 187,133,101]
    --throttle=<throttle>        Fix throttle [default: 0.2]
"""

import logging
from docopt import docopt

import donkeycar as dk

from xebikart.parts import (add_throttle, add_steering, add_pi_camera, add_logger,
                            add_mqtt_image_base64_publisher, add_mqtt_metadata_publisher,
                            add_mqtt_remote_mode_subscriber, add_brightness_detector,
                            add_color_box_detector)
from xebikart.parts.tflite import AsyncBufferedAction
from xebikart.parts.image import ImageTransformation
from xebikart.parts.joystick import Joystick
from xebikart.parts.keras import OneOutputModel

import xebikart.images.transformer as image_transformer

import tensorflow as tf

import numpy as np

tf.compat.v1.enable_eager_execution()


def drive(cfg, args):
    vehicle = dk.vehicle.Vehicle()

    # Connect pi camera
    print("Loading pi camera...")
    add_pi_camera(vehicle, cfg, 'cam/image_array')

    print("Loading joystick...")
    joystick = Joystick(
        throttle_scale=cfg.JOYSTICK_MAX_THROTTLE,
        steering_scale=cfg.JOYSTICK_STEERING_SCALE
    )
    vehicle.add(joystick, outputs=['js/steering', 'js/throttle', 'js/actions'], threaded=True)

    # Steering model
    print("Loading steering model...")
    steering_model_path = args["--steering-model"]
    add_steering_model(vehicle, steering_model_path, 'cam/image_array', 'ai/steering')

    # Exit model
    print("Loading exit model...")
    exit_model_path = args["--exit-model"]
    add_exit_model(vehicle, exit_model_path, 'cam/image_array', 'exit/buffer')

    # Brightness
    print("Loading brightness detector...")
    brightness_buffer_size = 10
    add_brightness_detector(vehicle, brightness_buffer_size, 'cam/image_array', 'brightness/buffer')

    # Add color box detection
    print("Loading brightness detector...")
    color_to_detect = [int(v) for v in args["--color"].split(",")]
    add_color_box_detector(vehicle, color_to_detect, 30, 10, 'cam/image_array', 'detect/box')

    # Keynote driver
    print("Loading keynote driver...")
    throttle = float(args["--throttle"])
    driver = KeynoteDriverV2(default_throttle=throttle, exit_threshold=1., brightness_threshold=50000 * brightness_buffer_size)
    vehicle.add(driver,
                inputs=['js/steering', 'js/throttle', 'js/actions', 'ai/steering', 'detect/box', 'exit/buffer', 'brightness/buffer'],
                outputs=['pilot/steering', 'pilot/throttle', 'pilot/mode'])

    add_steering(vehicle, cfg, 'pilot/steering')
    add_throttle(vehicle, cfg, 'pilot/throttle')

    print("Log to rabbitmq")
    add_mqtt_image_base64_publisher(vehicle, cfg, cfg.RABIITMQ_VIDEO_TOPIC, 'cam/image_array')
    add_mqtt_metadata_publisher(vehicle, cfg, cfg.RABBITMQ_TOPIC, cfg.CAR_ID,
                                steering="pilot/steering", throttle="pilot/throttle", mode="pilot/mode")
    add_mqtt_remote_mode_subscriber(vehicle, cfg, cfg.RABBITMQ_TOPIC + "/cars/" + str(cfg.CAR_ID), cfg.CAR_ID,
                                    'mqtt/mode')

    #add_logger(vehicle, 'detect/_sum', 'detect/_sum')
    #add_logger(vehicle, 'mqtt/mode', 'mqtt/mode')

    print("Starting vehicle...")
    vehicle.start(
        rate_hz=cfg.DRIVE_LOOP_HZ,
        max_loop_count=cfg.MAX_LOOPS
    )


class KeynoteDriverV2:
    def __init__(self, default_throttle, exit_threshold, brightness_threshold):
        self.default_throttle = default_throttle
        self.current_throttle = self.default_throttle
        self.exit_threshold = exit_threshold
        self.brightness_threshold = brightness_threshold
        self.emergency_sequence = ([-0.4] * 5) + ([0.] * 20)
        self.current_emergency_sequence = []
        self.safe_mode = True

    def is_emergency_mode(self):
        return len(self.current_emergency_sequence) > 0

    def initiate_emergency_mode(self):
        self.safe_mode = True
        self.current_throttle = self.default_throttle
        self.current_emergency_sequence = self.emergency_sequence.copy()

    def run(self, user_steering, user_throttle, user_buttons, ai_steering, detect_box, exit_buffer, brightness_buffer):
        if self.is_emergency_mode():
            return 0., self.current_emergency_sequence.pop(), "emergency_stop"
        elif self.safe_mode:
            if Joystick.SQUARE in user_buttons:
                self.safe_mode = False
            return user_steering, user_throttle, "safe_mode"
        else:
            # bottom left corner
            x = detect_box[1]
            y = detect_box[2]
            if (Joystick.CROSS in user_buttons
                    or np.sum(exit_buffer) > self.exit_threshold
                    or np.sum(brightness_buffer) < self.brightness_threshold):
                self.initiate_emergency_mode()
            if Joystick.R1 in user_buttons:
                self.current_throttle += 0.01
            if Joystick.L1 in user_buttons:
                self.current_throttle -= 0.01

            return ai_steering, self.current_throttle, "ai_v2_mode"


def add_exit_model(vehicle, exit_model_path, camera_input, exit_model_output):
    image_transformation = ImageTransformation([
        image_transformer.normalize,
        image_transformer.generate_crop_fn(0, 40, 160, 80),
        tf.image.rgb_to_grayscale
    ])
    vehicle.add(image_transformation, inputs=[camera_input], outputs=['exit/_image'])
    # Predict on transformed image
    exit_model = AsyncBufferedAction(model_path=exit_model_path, buffer_size=4, rate_hz=4.)
    vehicle.add(exit_model, inputs=['exit/_image'], outputs=[exit_model_output], threaded=True)


def add_steering_model(vehicle, steering_path, camera_input, steering_model_output):
    image_transformation = ImageTransformation([
        image_transformer.normalize,
        image_transformer.generate_crop_fn(0, 40, 160, 80),
        image_transformer.edges
    ])
    vehicle.add(image_transformation, inputs=[camera_input], outputs=['ai/_image'])
    # Predict on transformed image
    steering_model = OneOutputModel()
    steering_model.load(steering_path)
    vehicle.add(steering_model, inputs=['ai/_image'], outputs=[steering_model_output])


if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config()
    logging.basicConfig(level=cfg.LOG_LEVEL, format=cfg.LOG_FORMAT, handlers=[logging.StreamHandler()])
    drive(cfg, args)
