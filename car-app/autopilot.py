#!/usr/bin/env python3

"""
Usage:
    autopilot.py --model=<model_path>

Options:
    -h --help           Show this screen.
    --model=<path>      Path to h5 model (steering + throttle) (.h5)

"""

import logging
from docopt import docopt

import donkeycar as dk

from xebikart_app import add_publish_to_mqtt, add_sensors, add_controller, \
    add_throttle, add_steering, add_timestamp, add_pi_camera, add_pilot

from xebikart_app.parts.keras import PilotModel
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
    add_image_transformation(vehicle, 'cam/image_array', 'transformed/image_array')
    add_autopilot_model(vehicle, model_path, 'transformed/image_array', 'ai/steering', 'ai/throttle')

    add_pilot(vehicle, 'user/mode',
              'user/steering', 'user/throttle',
              'ai/steering', 'ai/throttle',
              'pilot/steering', 'pilot/throttle')

    add_steering(vehicle, 'pilot/angle', cfg)
    add_throttle(vehicle, 'pilot/throttle', cfg)

    # Add sensors
    add_timestamp(vehicle)
    add_sensors(vehicle)

    # Publish to mqtt
    add_publish_to_mqtt(vehicle, 'pilot/angle', 'pilot/throttle')

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


def add_autopilot_model(vehicle, model_path, image_input, steering_output, throttle_output):
    pilot_model = PilotModel()
    pilot_model.load(model_path)
    vehicle.add(
        pilot_model,
        inputs=[
            image_input
        ],
        outputs=[
            steering_output,
            throttle_output
        ]
    )


if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config()
    logging.basicConfig(level=cfg.LOG_LEVEL, format=cfg.LOG_FORMAT, handlers=[logging.StreamHandler()])
    drive(cfg, args)
