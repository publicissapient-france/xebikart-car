#!/usr/bin/env python3

"""
Usage:
    manage.py [--model=<model>]

Options:
    -h --help        Show this screen.
    --tub TUBPATHS   List of paths to tubs. Comma separated. Use quotes to use wildcards. ie "~/tubs/*"
"""

import os
from docopt import docopt

import donkeycar as dk
from donkeycar.parts.camera import PiCamera
from donkeycar.parts.transform import Lambda
from donkeycar.parts.keras import KerasLinear
from donkeycar.parts.actuator import PCA9685, PWMSteering, PWMThrottle
from donkeycar.parts.datastore import TubGroup, TubWriter
from donkeycar.parts.clock import Timestamp
from donkeypart_ps3_controller import PS3JoystickController

from lidar import RPLidar, BreezySLAM
import mqttClient

from driver import Driver


def drive(cfg, model_path=None):
    V = dk.vehicle.Vehicle()

    clock = Timestamp()
    V.add(
        clock,
        outputs=[
            'timestamp'
        ]
    )

    camera = PiCamera(resolution=cfg.CAMERA_RESOLUTION)
    V.add(
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
    V.add(
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

    V.add(
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

    driver = Driver()
    V.add(
        driver,
        inputs=[
            'user/mode',
            'user/angle',
            'user/throttle',
            'pilot/angle',
            'pilot/throttle',
            'car/x',
            'car/y',
            'car/angle'
        ],
        outputs=[
            'angle',
            'throttle',
            'run_pilot'
        ]
    )

    steering = PWMSteering(
        controller=PCA9685(cfg.STEERING_CHANNEL),
        left_pulse=cfg.STEERING_LEFT_PWM,
        right_pulse=cfg.STEERING_RIGHT_PWM
    )
    V.add(
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
    V.add(
        throttle,
        inputs=[
            'throttle'
        ]
    )

    lidar = RPLidar()
    V.add(
        lidar,
        outputs=[
            'lidar/distances',
            'lidar/angles'
        ],
        threaded=True
    )

    breezy_slam = BreezySLAM()
    V.add(
        breezy_slam,
        inputs=[
            'lidar/distances',
            'lidar/angles'
        ],
        outputs=[
            'car/x',
            'car/y',
            'car/angle',
        ]
    )

    inputs = ['cam/image_array', 'user/angle', 'user/throttle', 'user/mode', 'timestamp']
    types = ['image_array', 'float', 'float', 'str', 'str']
    tub_writer = TubWriter(path=cfg.TUB_PATH, inputs=inputs, types=types)
    V.add(
        tub_writer,
        inputs=inputs,
        run_condition='recording'
    )

    # MQTT
    mqtt_publisher = mqttClient.MqttPublisher()
    V.add(
        mqtt_publisher,
        inputs=['user/throttle'],
        outputs=['user/throttle'],
        threaded=True
    )

    V.start(
        rate_hz=cfg.DRIVE_LOOP_HZ,
        max_loop_count=cfg.MAX_LOOPS
    )


if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config()
    drive(cfg, model_path=args['--model'])
