#!/usr/bin/env python3

"""
Usage:
    record.py --steps=<nb_steps>

Options:
    -h --help                   Show this screen.
    --steps=<steps>             Number of steps to record
"""

import os
import logging
import tarfile
from docopt import docopt

import donkeycar as dk

from donkeycar.parts.datastore import TubHandler

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

    add_steering(vehicle, cfg, 'user/angle')
    add_throttle(vehicle, cfg, 'user/throttle')

    print("Loading TubWriter")
    tub_handler = TubHandler("tubes/")
    tub_writer = tub_handler.new_tub_writer(inputs=['cam/image_array', 'user/angle', 'user/throttle'],
                                            types=['image_array', 'float', 'float'])
    vehicle.add(tub_writer, inputs=['cam/image_array', 'user/angle', 'user/throttle'])

    # Stop car after x steps
    vehicle.add(ExitAfterSteps(int(args["--steps"])))

    print("Starting vehicle...")
    vehicle.start(
        rate_hz=cfg.DRIVE_LOOP_HZ,
        max_loop_count=cfg.MAX_LOOPS
    )

    save_path = os.path.basename(tub_writer.path)
    print(f"Create archive for run {tub_writer.path} in {save_path}.tar.gz")
    with tarfile.open(name=f"{save_path}.tar.gz", mode='w:gz') as tar:
        tar.add(tub_writer.path, arcname=os.path.basename(tub_writer.path))


class ExitAfterSteps:
    def __init__(self, steps):
        self.steps = steps

    def run(self):
        self.steps -= 1
        if self.steps < 0:
            raise KeyboardInterrupt


if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config()
    logging.basicConfig(level=cfg.LOG_LEVEL, format=cfg.LOG_FORMAT, handlers=[logging.StreamHandler()])
    drive(cfg, args)
