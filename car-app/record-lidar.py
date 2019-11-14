#!/usr/bin/env python3

"""
Usage:
    record-lidar.py --steps=<nb_steps> --throttle=<throttle>

Options:
    -h --help                   Show this screen.
    --steps=<steps>             Number of steps to record
    --throttle<throttle>        Fix throttle
"""

import os
import logging
import tarfile
from docopt import docopt

import donkeycar as dk

from donkeycar.parts.datastore import TubHandler
from donkeycar.parts.transform import Lambda

from xebikart.parts import add_throttle, add_steering, add_pi_camera, add_logger
from xebikart.parts.joystick import Joystick

import tensorflow as tf

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
    vehicle.add(joystick, outputs=['user/angle', 'user/throttle', 'js/actions'], threaded=True)
    # Add fix throttle
    fix_throttle = Lambda(lambda: args["--throttle"])
    vehicle.add(fix_throttle, outputs=['fix/throttle'])

    print("Add lidar sensor")
    add_lidar_sensor(vehicle, cfg, "lidar/output")
    add_logger(vehicle, "lidar/output", "lidar/output")

    add_steering(vehicle, cfg, 'user/angle')
    add_throttle(vehicle, cfg, 'fix/throttle')

    print("Loading TubWriter")
    tub_handler = TubHandler("tubes/")
    tub_writer = tub_handler.new_tub_writer(inputs=['cam/image_array', 'user/angle', 'user/throttle', 'lidar/output'],
                                            types=['image_array', 'float', 'float', 'float'])

    vehicle.add(tub_writer, inputs=['cam/image_array', 'user/angle', 'fix/throttle', 'lidar/output'])

    # Stop car after x steps
    vehicle.add(ExitAfterSteps(int(args["--steps"])))

    print("Starting vehicle...")
    vehicle.start(
        rate_hz=cfg.DRIVE_LOOP_HZ,
        max_loop_count=cfg.MAX_LOOPS
    )

    save_path = os.path.basename(tub_writer.path)
    print("Create archive for run {} in {}.tar.gz".format(tub_writer.path, save_path))
    with tarfile.open(name="{}.tar.gz".format(save_path), mode='w:gz') as tar:
        tar.add(tub_writer.path, arcname=os.path.basename(tub_writer.path))


class ExitAfterSteps:
    def __init__(self, steps):
        self.steps = steps

    def run(self):
        self.steps -= 1
        if self.steps < 0:
            raise KeyboardInterrupt


def add_lidar_sensor(vehicle, cfg, lidar_output):
    from xebikart.parts.lidar import RPLidar, LidarProcessedMeasures

    lidar = RPLidar()
    vehicle.add(
        lidar,
        outputs=[
            'lidar/scan'
        ],
        threaded=True
    )
    breezy_slam = LidarProcessedMeasures()
    vehicle.add(
        breezy_slam,
        inputs=[
            'lidar/scan'
        ],
        outputs=[
            lidar_output
        ]
    )


if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config()
    logging.basicConfig(level=cfg.LOG_LEVEL, format=cfg.LOG_FORMAT, handlers=[logging.StreamHandler()])
    drive(cfg, args)
