#!/usr/bin/env python3

"""
Usage:
    keynote.py --steering-model=<steering_model_path> --exit-model=<exit_model_path> --detect-model=<detect_model_path> [--throttle=<throttle>]

Options:
    -h --help                    Show this screen.
    --steering-model=<path>      Path to h5 model (steering only) (.h5)
    --throttle=<throttle>        Fix throttle [default: 0.2]
    --exit-model=<path>          Path to tflite model (exit) (.tflite)
    --detect-model=<path>        Path to tflite model (detect) (.tflite)
"""

import logging
from docopt import docopt

import donkeycar as dk
from donkeycar.parts.transform import Lambda

from xebikart.parts import add_throttle, add_steering, add_pi_camera, add_logger
from xebikart.parts.keras import OneOutputModel
from xebikart.parts.tflite import AsyncBufferedAction
from xebikart.parts.image import ImageTransformation
from xebikart.parts.joystick import KeynoteJoystick
from xebikart.parts.buffers import Rolling, Sum
from xebikart.parts.condition import HigherThan, LessThan
from xebikart.parts.driver import KeynoteDriver

import xebikart.images.transformer as image_transformer

import tensorflow as tf

tf.compat.v1.enable_eager_execution()


def drive(cfg, args):
    vehicle = dk.vehicle.Vehicle()

    # Connect pi camera
    print("Loading pi camera...")
    add_pi_camera(vehicle, cfg, 'cam/image_array')

    print("Loading joystick...")
    joystick = KeynoteJoystick(
        throttle_scale=cfg.JOYSTICK_MAX_THROTTLE,
        steering_scale=cfg.JOYSTICK_STEERING_SCALE
    )
    vehicle.add(joystick, outputs=['js/steering', 'js/throttle', 'js/actions'], threaded=True)

    # Steering model
    print("Loading steering model...")
    steering_model_path = args["--steering-model"]
    throttle = args["--throttle"]
    add_steering_model(vehicle, steering_model_path, 'cam/image_array', 'ai/steering')

    # Detect model
    print("Loading detect model...")
    detect_model_path = args["--detect-model"]
    add_detect_model(vehicle, detect_model_path, 'cam/image_array', 'detect/buffer')

    # Exit model
    print("Loading exit model...")
    exit_model_path = args["--exit-model"]
    add_exit_model(vehicle, exit_model_path, 'cam/image_array', 'exit/buffer')

    # Brightness
    print("Loading brightness detector...")
    add_brightness_detector(vehicle, 'cam/image_array', 'brightness/buffer')

    # Keynote driver
    print("Loading keynote driver...")
    driver = KeynoteDriver(
        throttle_scale=cfg.JOYSTICK_MAX_THROTTLE
    )
    vehicle.add(driver,
                inputs=['js/steering', 'js/throttle', 'js/actions',
                        'ai/steering', 'detect/buffer', 'exit/buffer', 'brightness/buffer'],
                outputs=['pilot/steering', 'pilot/throttle'])

    add_steering(vehicle, cfg, 'pilot/steering')
    add_throttle(vehicle, cfg, 'pilot/throttle')

    #add_logger(vehicle, 'detect/_sum', 'detect/_sum')
    #add_logger(vehicle, 'exit/_sum', 'exit/_sum')

    print("Starting vehicle...")
    vehicle.start(
        rate_hz=cfg.DRIVE_LOOP_HZ,
        max_loop_count=cfg.MAX_LOOPS
    )


def add_exit_model(vehicle, exit_model_path, camera_input, exit_model_output):
    image_transformation = ImageTransformation([
        image_transformer.normalize,
        image_transformer.generate_crop_fn(30, 80, 80, 30),
        tf.image.rgb_to_grayscale
    ])
    vehicle.add(image_transformation, inputs=[camera_input], outputs=['exit/_image'])
    # Predict on transformed image
    exit_model = AsyncBufferedAction(model_path=exit_model_path, buffer_size=4, rate_hz=4.)
    vehicle.add(exit_model, inputs=['exit/_image'], outputs=[exit_model_output], threaded=True)


def add_detect_model(vehicle, detect_model_path, camera_input, detect_model_output):
    image_transformation = ImageTransformation([
        image_transformer.normalize,
        tf.image.rgb_to_grayscale
    ])
    vehicle.add(image_transformation, inputs=[camera_input], outputs=['detect/_image'])
    # Predict on transformed image
    detection_model = AsyncBufferedAction(model_path=detect_model_path, buffer_size=4, rate_hz=4.)
    vehicle.add(detection_model, inputs=['detect/_image'], outputs=[detect_model_output], threaded=True)


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


def add_brightness_detector(vehicle, camera_input, brightness_output):
    image_transformation = ImageTransformation([
        lambda x: tf.dtypes.cast(x, "int32"),
        tf.math.reduce_sum
    ])
    vehicle.add(image_transformation, inputs=[camera_input], outputs=['brightness/_reduce'])
    # Rolling buffer n last predictions
    buffer = Rolling(buffer_size=10)
    vehicle.add(buffer, inputs=['brightness/_reduce'], outputs=[brightness_output])


if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config()
    logging.basicConfig(level=cfg.LOG_LEVEL, format=cfg.LOG_FORMAT, handlers=[logging.StreamHandler()])
    drive(cfg, args)
