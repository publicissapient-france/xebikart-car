#!/usr/bin/env python3

"""
Usage:
    steeringpilot.py --model=<model_path> [--throttle=<throttle>]

Options:
    -h --help               Show this screen.
    --model=<path>          Path to h5 model (steering only) (.h5)
    --throttle=<throttle>   Fix throttle [default: 0.2]
"""

import logging
from docopt import docopt

import donkeycar as dk
from donkeycar.parts.transform import Lambda

from xebikart_app import add_controller, \
    add_throttle, add_steering, add_pi_camera, add_pilot, add_logger

from xebikart_app.parts.keras import OneOutputModel
from xebikart_app.parts.image import ImageTransformation

import xebikart.images.transformer as image_transformer

import tensorflow as tf

tf.compat.v1.enable_eager_execution()


def drive(cfg, args):
    vehicle = dk.vehicle.Vehicle()

    # Connect pi camera
    add_pi_camera(vehicle, cfg, 'cam/image_array')

    # Keep it for emergency stop (cross)
    add_controller(vehicle, cfg, 'user/steering', 'user/throttle', 'user/mode', 'recording')

    # Model
    model_path = args["--model"]
    throttle = args["--throttle"]
    add_image_transformation(vehicle, 'cam/image_array', 'transformed/image_array')
    add_steering_model(vehicle, model_path, throttle, 'transformed/image_array', 'ai/steering', 'ai/throttle')

    add_pilot(vehicle, 'user/mode',
              'user/steering', 'user/throttle',
              'ai/steering', 'ai/throttle',
              'pilot/steering', 'pilot/throttle')
    add_steering(vehicle, cfg, 'pilot/steering')
    add_throttle(vehicle, cfg, 'pilot/throttle')

    add_logger(vehicle, 'pilot/steering', 'pilot/steering')
    add_logger(vehicle, 'pilot/throttle', 'pilot/throttle')

    vehicle.start(
        rate_hz=cfg.DRIVE_LOOP_HZ,
        max_loop_count=cfg.MAX_LOOPS
    )


def add_image_transformation(vehicle, camera_input, transformation_output):
    image_transformation = ImageTransformation([
        image_transformer.normalize,
        image_transformer.generate_crop_fn(0, 40, 160, 80),
        image_transformer.edges
    ])
    vehicle.add(
        image_transformation,
        inputs=[
            camera_input
        ],
        outputs=[
            transformation_output
        ]
    )


def add_steering_model(vehicle, steering_path, fix_throttle, image_input, ai_steering_output, ai_throttle_output):
    steering_model = OneOutputModel()
    steering_model.load(steering_path)
    vehicle.add(
        steering_model,
        inputs=[
            image_input
        ],
        outputs=[
            ai_steering_output
        ]
    )
    fix_throttle_lb = Lambda(lambda: fix_throttle)
    vehicle.add(
        fix_throttle_lb,
        outputs=[
            ai_throttle_output
        ]
    )


if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config()
    logging.basicConfig(level=cfg.LOG_LEVEL, format=cfg.LOG_FORMAT, handlers=[logging.StreamHandler()])
    drive(cfg, args)
