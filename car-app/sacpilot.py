#!/usr/bin/env python3

"""
Usage:
    sacpilot.py --model=<model_path> --vae=<vae_path>

Options:
    -h --help          Show this screen.
    --model=<path>     Path to soft actor critical model (.pkl)
    --vae=<path>       Path to variational auto encoder model (.h5)
"""

import logging
from docopt import docopt

import donkeycar as dk

from xebikart_app import add_controller, \
    add_throttle, add_steering, add_pi_camera, add_pilot, add_logger

from xebikart_app.parts.rl import SoftActorCriticalModel
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
    vae_path = args["--vae"]
    add_image_transformation(vehicle, 'cam/image_array', 'transformed/image_array')
    add_image_embedding(vehicle, vae_path, 'transformed/image_array', 'embedded/image_array')
    add_soft_actor_critical_model(vehicle, model_path, 'embedded/image_array', 'ai/steering', 'ai/throttle')

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


def add_image_embedding(vehicle, vae_path, image_input, embedded_output):
    vae = tf.keras.models.load_model(vae_path)
    image_embedding = ImageTransformation([
        image_transformer.generate_vae_fn(vae)
    ])
    vehicle.add(
        image_embedding,
        inputs=[
            image_input
        ],
        outputs=[
            embedded_output
        ]
    )


def add_soft_actor_critical_model(vehicle, sac_path, embedded_input, steering_output, throttle_output):
    soft_actor_critical_model = SoftActorCriticalModel(sac_path)
    vehicle.add(
        soft_actor_critical_model,
        inputs=[
            embedded_input
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
