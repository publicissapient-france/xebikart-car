#!/usr/bin/env python3
"""
Scripts to drive a donkey 2 car with a sac model

Usage:
    enjoy_sac_model.py --vae=<vae> --sac=<sac> [--record]

Options:
    -h --help           Show this screen.
    --model MODELPATH   Path to tensorflow model
"""
from docopt import docopt

import donkeycar as dk
from donkeycar.parts.camera import PiCamera
from donkeycar.parts.transform import Lambda
from donkeycar.parts.actuator import PCA9685, PWMSteering, PWMThrottle
from donkeycar.parts.clock import Timestamp

from xebikart.tf import SimpleTensorFlow


def drive(cfg, model):
    V = dk.vehicle.Vehicle()

    clock = Timestamp()
    V.add(clock, outputs=['timestamp'])

    cam = PiCamera(resolution=cfg.CAMERA_RESOLUTION)
    V.add(cam, outputs=['cam/image_array'], threaded=True)

    def model_with_fix_throttle(_model, _throttle):
        def run(img_arr):
            return _model.predict(img_arr), _throttle
        return run

    auto_pilot_action = Lambda(model_with_fix_throttle(model, _throttle=0.20))

    V.add(auto_pilot_action,
          inputs=['cam/image_array'],
          outputs=['angle', 'throttle'])

    steering_controller = PCA9685(cfg.STEERING_CHANNEL)
    steering = PWMSteering(controller=steering_controller,
                           left_pulse=cfg.STEERING_LEFT_PWM,
                           right_pulse=cfg.STEERING_RIGHT_PWM)

    throttle_controller = PCA9685(cfg.THROTTLE_CHANNEL)
    throttle = PWMThrottle(controller=throttle_controller,
                           max_pulse=cfg.THROTTLE_FORWARD_PWM,
                           zero_pulse=cfg.THROTTLE_STOPPED_PWM,
                           min_pulse=cfg.THROTTLE_REVERSE_PWM)

    V.add(steering, inputs=['angle'])
    V.add(throttle, inputs=['throttle'])

    def print_angle_throttle(angle, throttle):
        print("Angle: %s - Throttle: %s" % (str(angle), str(throttle)))

    V.add(Lambda(print_angle_throttle),
          inputs=['angle', 'throttle'])

    # run the vehicle
    V.start(rate_hz=cfg.DRIVE_LOOP_HZ,
            max_loop_count=cfg.MAX_LOOPS)


if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config()

    model = SimpleTensorFlow(model_path=args['--model'])
    drive(cfg, model)
