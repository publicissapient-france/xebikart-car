#!/usr/bin/env python3

"""
Usage:
    manage.py
    manage.py --pilot-model=<model_path>
    manage.py --steering-model=<model_path> [--throttle=<throttle>]
    manage.py --sac-model=<model_path> --vae-model=<vae_path>

Options:
    -h --help                   Show this screen.
    --pilot-model=<path>        Path to pilot model.
    --steering-model=<path>     Path to h5 model (steering only) (.h5)
    --throttle=<throttle>       Fix throttle [default: 0.2]
    --sac-model=<path>          Path to soft actor critical model (.pkl)
    --vae-model=<path>          Path to variational auto encoder (.h5)
"""

import os
import logging
from docopt import docopt

import donkeycar as dk
from donkeycar.parts.camera import PiCamera
from donkeycar.parts.actuator import PCA9685, PWMSteering, PWMThrottle
from donkeycar.parts.datastore import TubWriter
from donkeycar.parts.clock import Timestamp
from donkeycar.parts.transform import Lambda
from donkeypart_ps3_controller import PS3JoystickController

from xebikart_app.parts.driver import Driver
from xebikart_app.parts.lidar import RPLidar, BreezySLAM
from xebikart_app.parts.imu import Mpu6050
from xebikart_app.parts.mqtt import MQTTClient
from xebikart_app.parts.keras import PilotModel, SteeringModel
from xebikart_app.parts.rl import SoftActorCriticalModel
from xebikart_app.parts.image import ImageTransformation

import xebikart.images.transformer as image_transformer

import tensorflow as tf

tf.compat.v1.enable_eager_execution()


def drive(cfg, args):
    vehicle = dk.vehicle.Vehicle()

    clock = Timestamp()
    vehicle.add(
        clock,
        outputs=[
            'timestamp'
        ]
    )

    camera = PiCamera(resolution=cfg.CAMERA_RESOLUTION)
    vehicle.add(
        camera,
        outputs=[
            'cam/image_array'
        ],
        threaded=True
    )

    controller = PS3JoystickController(
        throttle_scale=cfg.JOYSTICK_MAX_THROTTLE,
        steering_scale=cfg.JOYSTICK_STEERING_SCALE,
        auto_record_on_throttle=cfg.AUTO_RECORD_ON_THROTTLE
    )
    vehicle.add(
        controller,
        outputs=[
            'user/angle',
            'user/throttle',
            'user/mode',
            'recording'
        ],
        threaded=True
    )

    if args["--pilot-model"] is not None:
        add_image_transformation(vehicle)
        add_pilot_model(vehicle, args["--pilot-model"])
    elif args["--steering-model"] is not None:
        add_image_transformation(vehicle)
        add_steering_model(vehicle, args["--steering-model"], float(args["throttle"]))
    elif args["--sac-model"] is not None:
        add_image_transformation(vehicle)
        add_image_embedding(vehicle, args["--vae-model"])
        add_soft_actor_critical_model(vehicle, args["--sac-model"])

    driver = Driver()
    vehicle.add(
        driver,
        inputs=[
            'user/mode',
            'user/angle',
            'user/throttle',
            'pilot/angle',
            'pilot/throttle',
            'car/x',
            'car/y',
            'car/z',
            'car/angle',
            'car/dx',
            'car/dy',
            'car/dz',
            'car/tx',
            'car/ty',
            'car/tz'
        ],
        outputs=[
            'angle',
            'throttle',
            'run_pilot',
            'imu_enabled',
            'lidar_enabled'
        ]
    )

    steering = PWMSteering(
        controller=PCA9685(cfg.STEERING_CHANNEL),
        left_pulse=cfg.STEERING_LEFT_PWM,
        right_pulse=cfg.STEERING_RIGHT_PWM
    )
    vehicle.add(
        steering,
        inputs=[
            'angle'
        ]
    )

    throttle = PWMThrottle(
        controller=PCA9685(cfg.THROTTLE_CHANNEL),
        max_pulse=cfg.THROTTLE_FORWARD_PWM,
        zero_pulse=cfg.THROTTLE_STOPPED_PWM,
        min_pulse=cfg.THROTTLE_REVERSE_PWM
    )
    vehicle.add(
        throttle,
        inputs=[
            'throttle'
        ]
    )

    imu = Mpu6050()
    vehicle.add(
        imu,
        outputs=[
            'car/dx',
            'car/dy',
            'car/dz',
            'car/tx',
            'car/ty',
            'car/tz'
        ],
        threaded=True,
        run_condition='imu_enabled'
    )

    lidar = RPLidar()
    vehicle.add(
        lidar,
        outputs=[
            'lidar/distances',
            'lidar/angles'
        ],
        threaded=True,
        run_condition='lidar_enabled'
    )

    breezy_slam = BreezySLAM()
    vehicle.add(
        breezy_slam,
        inputs=[
            'lidar/distances',
            'lidar/angles'
        ],
        outputs=[
            'car/x',
            'car/y',
            'car/z',
            'car/angle'
        ],
        run_condition='lidar_enabled'
    )

    inputs = ['cam/image_array', 'user/angle', 'user/throttle', 'user/mode', 'timestamp']
    types = ['image_array', 'float', 'float', 'str', 'str']
    tub_writer = TubWriter(path=cfg.TUB_PATH, inputs=inputs, types=types)
    vehicle.add(
        tub_writer,
        inputs=inputs,
        run_condition='recording'
    )

    mqtt_client = MQTTClient()
    vehicle.add(
        mqtt_client,
        inputs=[
            'user/mode',
            'user/angle',
            'user/throttle',
            'car/x',
            'car/y',
            'car/z',
            'car/angle',
            'car/dx',
            'car/dy',
            'car/dz',
            'car/tx',
            'car/ty',
            'car/tz'
        ],
        outputs=[
            'remote/mode'
        ],
        threaded=True
    )

    vehicle.start(
        rate_hz=cfg.DRIVE_LOOP_HZ,
        max_loop_count=cfg.MAX_LOOPS
    )


def add_soft_actor_critical_model(vehicle, sac_path):
    soft_actor_critical_model = SoftActorCriticalModel(sac_path)
    vehicle.add(
        soft_actor_critical_model,
        inputs=[
            'embedded/image_array'
        ],
        outputs=[
            'pilot/angle',
            'pilot/throttle'
        ],
        run_condition='run_pilot'
    )


def add_image_embedding(vehicle, vae_path):
    vae = tf.keras.models.load_model(vae_path)
    image_embedding = ImageTransformation([
        image_transformer.generate_vae_fn(vae)
    ])
    vehicle.add(
        image_embedding,
        inputs=[
            'transformed/image_array'
        ],
        outputs=[
            'embedded/image_array'
        ]
    )


def add_pilot_model(vehicle, model_path):
    pilot_model = PilotModel()
    pilot_model.load(model_path)
    vehicle.add(
        pilot_model,
        inputs=[
            'transformed/image_array'
        ],
        outputs=[
            'pilot/angle',
            'pilot/throttle'
        ],
        run_condition='run_pilot'
    )


def add_steering_model(vehicle, steering_path, fix_throttle):
    steering_model = SteeringModel()
    steering_model.load(steering_path)
    vehicle.add(
        steering_model,
        inputs=[
            'transformed/image_array'
        ],
        outputs=[
            'pilot/angle'
        ],
        run_condition='run_pilot'
    )
    fix_throttle_lb = Lambda(lambda: fix_throttle)
    vehicle.add(
        fix_throttle_lb,
        outputs=[
            'pilot/throttle'
        ],
        run_condition='run_pilot'
    )


def add_image_transformation(vehicle):
    image_transformation = ImageTransformation([
        image_transformer.normalize,
        image_transformer.generate_crop_fn(0, 40, 160, 80),
        image_transformer.edges
    ])
    vehicle.add(
        image_transformation,
        inputs=[
            'cam/image_array'
        ],
        outputs=[
            'transformed/image_array'
        ]
    )


if __name__ == '__main__':
    args = docopt(__doc__)
    print(args)
    cfg = dk.load_config()
    logging.basicConfig(level=cfg.LOG_LEVEL, format=cfg.LOG_FORMAT, handlers=[logging.StreamHandler()])
    drive(cfg, args)
