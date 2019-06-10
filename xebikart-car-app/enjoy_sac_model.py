#!/usr/bin/env python3
"""
Scripts to drive a donkey 2 car with a sac model

Usage:
    enjoy_sac_model.py --vae=<vae> --sac=<sac> [--record]

Options:
    -h --help        Show this screen.
    --vae VAEPATH    Path to a VAE model
    --sac SACPATH    Path to a SAC model
    --record         Record the run
"""
from docopt import docopt

import donkeycar as dk
from donkeycar.parts.camera import PiCamera
from donkeycar.parts.transform import Lambda
from donkeycar.parts.actuator import PCA9685, PWMSteering, PWMThrottle
from donkeycar.parts.datastore import TubWriter
from donkeycar.parts.clock import Timestamp

from xebikart.rl import SACModel


def drive(cfg, model, record=False):
    V = dk.vehicle.Vehicle()

    clock = Timestamp()
    V.add(clock, outputs=['timestamp'])

    cam = PiCamera(resolution=cfg.CAMERA_RESOLUTION)
    V.add(cam, outputs=['cam/image_array'], threaded=True)

    V.add(model,
          inputs=['cam/image_array'],
          outputs=['pilot/angle', 'pilot/throttle'])

    def clip_throttle(min_throttle, max_throttle):
        def run(_steering, _throttle):
            return _steering, max(min_throttle, min(max_throttle, _throttle))
        return run

    def fix_throttle(_throttle):
        def run(_steering, _):
            return _steering, _throttle
        return run

    clip_action = Lambda(clip_throttle(min_throttle=0.20, max_throttle=0.30))
    fix_throttle_action = Lambda(fix_throttle(0.2))
    V.add(fix_throttle_action,
          inputs=['pilot/angle', 'pilot/throttle'],
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
    # single tub
    if record:
        # add tub to save data
        inputs = ['cam/image_array', 'user/angle', 'user/throttle', 'user/mode', 'timestamp']
        types = ['image_array', 'float', 'float', 'str', 'str']

        tub = TubWriter(path=cfg.TUB_PATH, inputs=inputs, types=types)
        V.add(tub, inputs=inputs)

    # run the vehicle
    V.start(rate_hz=cfg.DRIVE_LOOP_HZ,
            max_loop_count=cfg.MAX_LOOPS)


if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config()

    model = SACModel(vae_path=args['--vae'], sac_path=args['--sac'], n_command_history=20)
    drive(cfg, model, record=args['--record'])
