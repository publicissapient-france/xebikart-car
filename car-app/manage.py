#!/usr/bin/env python3

"""
Usage:
    manage.py [--model=<model>]

Options:
    -h --help        Show this screen.
    --tub TUBPATHS   List of paths to tubs. Comma separated. Use quotes to use wildcards. ie "~/tubs/*"
"""

import os
import logging
from docopt import docopt

import donkeycar as dk
from donkeycar.parts.camera import PiCamera
from donkeycar.parts.keras import KerasLinear
from donkeycar.parts.actuator import PCA9685, PWMSteering, PWMThrottle
from donkeycar.parts.datastore import TubWriter
from donkeycar.parts.clock import Timestamp
from donkeypart_ps3_controller import PS3JoystickController

from xebikart.parts.driver import Driver
from xebikart.parts.lidar import RPLidar, BreezySLAM
from xebikart.parts.imu import Mpu6050
from xebikart.parts.mqtt import MQTTClient


def drive(cfg, model_path=None):
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

    keras_linear = KerasLinear()
    if model_path:
        keras_linear.load(model_path)

    vehicle.add(
        keras_linear,
        inputs=[
            'cam/image_array'
        ],
        outputs=[
            'pilot/angle',
            'pilot/throttle'
        ],
        run_condition='run_pilot'
    )

    driver = Driver(cfg)
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


if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config()
    logging.basicConfig(level=cfg.LOG_LEVEL, format=cfg.LOG_FORMAT, handlers=[logging.StreamHandler()])
    drive(cfg, model_path=args['--model'])
