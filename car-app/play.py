#!/usr/bin/env python3

"""
Usage:
    keynote.py --model=<model_path> --exit-model=<exit_model_path> [--throttle=<throttle>]

Options:
    -h --help                    Show this screen.
    --model=<path>               Path to h5 model (steering only) (.h5)
    --throttle=<throttle>        Fix throttle [default: 0.2]
    --exit-model=<path>          Path to tflite model (exit) (.tflite)
"""

import logging
from docopt import docopt

import numpy as np

import donkeycar as dk
from donkeycar.parts.transform import Lambda

from xebikart.parts import add_throttle, add_steering, add_pi_camera, add_logger
from xebikart.parts.keras import PilotModel
from xebikart.parts.tflite import AsyncBufferedAction
from xebikart.parts.image import ImageTransformation

import xebikart.images.transformer as image_transformer

import tensorflow as tf

tf.compat.v1.enable_eager_execution()


def drive(cfg, args):
    vehicle = dk.vehicle.Vehicle()

    # Connect pi camera
    print("Loading pi camera...")
    add_pi_camera(vehicle, cfg, 'cam/image_array')

    # Steering model
    print("Loading model...")
    model_path = args["--model"]
    add_model(vehicle, model_path, 'cam/image_array', 'ai/steering', 'ai/throttle')

    # Exit model
    print("Loading exit model...")
    exit_model_path = args["--exit-model"]
    add_exit_model(vehicle, exit_model_path, 'cam/image_array', 'exit/should_stop')

    add_steering(vehicle, cfg, 'ai/steering')
    add_throttle(vehicle, cfg, 'ai/throttle')

    #add_logger(vehicle, 'detect/_sum', 'detect/_sum')
    #add_logger(vehicle, 'exit/_sum', 'exit/_sum')

    print("Starting vehicle...")
    vehicle.start(
        rate_hz=cfg.DRIVE_LOOP_HZ,
        max_loop_count=cfg.MAX_LOOPS
    )


def add_exit_model(vehicle, exit_model_path, camera_input, should_stop_output):
    image_transformation = ImageTransformation([
        image_transformer.normalize,
        image_transformer.generate_crop_fn(30, 80, 80, 30),
        tf.image.rgb_to_grayscale
    ])
    vehicle.add(image_transformation, inputs=[camera_input], outputs=['exit/_image'])
    # Predict on transformed image
    exit_model = AsyncBufferedAction(model_path=exit_model_path, buffer_size=4, rate_hz=4.)
    vehicle.add(exit_model, inputs=['exit/_image'], outputs=['exit/_buffer'], threaded=True)
    vehicle.add(Lambda(lambda x: np.sum(x) > 1.), inputs=['exit/_buffer'], outputs=[should_stop_output])


def add_model(vehicle, model_path, camera_input, ai_steering_output, ai_throttle_output):
    image_transformation = ImageTransformation([
        image_transformer.normalize,
        image_transformer.generate_crop_fn(0, 40, 160, 80),
        image_transformer.edges
    ])
    vehicle.add(image_transformation, inputs=[camera_input], outputs=['ai/_image'])
    # Predict on transformed image
    model = PilotModel()
    model.load(model_path)
    vehicle.add(model, inputs=['ai/_image'], outputs=[ai_steering_output, ai_throttle_output])


if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config()
    logging.basicConfig(level=cfg.LOG_LEVEL, format=cfg.LOG_FORMAT, handlers=[logging.StreamHandler()])
    drive(cfg, args)
