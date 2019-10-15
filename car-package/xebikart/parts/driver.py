import config

import numpy as np


class Driver:

    def run(
            self,
            mode,
            user_angle, user_throttle,  # from controller
            pilot_angle, pilot_throttle,  # from ML model
            x, y, z, angle,  # from lidar
            dx, dy, dz, tx, ty, tz  # from imu
    ):
        if mode == 'user':
            return user_angle, user_throttle, True, config.IMU_ENABLED, config.LIDAR_ENABLED
        else:
            return pilot_angle, pilot_throttle, False, config.IMU_ENABLED, config.LIDAR_ENABLED


class Mode:
    """
    Based on mode, returns user or ai outputs (steering and throttle)
    """
    def run(self, mode, user_steering, user_throttle, ai_steering, ai_throttle):
        if mode == 'user':
            return user_steering, user_throttle
        elif mode == 'local_angle':
            return ai_steering, user_throttle
        elif mode == 'local':
            return ai_steering, ai_throttle
        else:
            return 0., 0.


class KeynoteDriver:
    MODE_USER = "user"
    MODE_AI_STEERING = "ai_steering"
    MODE_AI = "ai"

    ES_START = 1
    ES_THROTTLE_NEG_ONE = 2
    ES_THROTTLE_POS_ONE = 3
    ES_THROTTLE_NEG_TWO = 4

    EMERGENCY_STOP = "emergency_stop"
    MODE_TOGGLE = "mode_toggle"

    def __init__(self, throttle_scale):
        self.default_modes = [KeynoteDriver.MODE_USER, KeynoteDriver.MODE_AI_STEERING, KeynoteDriver.MODE_AI]
        self.modes = self.default_modes
        # Emergency stop sequences
        self.es_sequence = [self.ES_START, self.ES_THROTTLE_NEG_ONE, self.ES_THROTTLE_POS_ONE, self.ES_THROTTLE_NEG_TWO]
        self.es_current_sequence = self.es_sequence
        # Bind actions to functions
        self.actions_fn = {
            KeynoteDriver.EMERGENCY_STOP: self.initiate_emergency_stop,
            KeynoteDriver.MODE_TOGGLE: self.roll_mode
        }
        # TODO: find a way to remove it
        self.throttle_scale = throttle_scale
        self.throttle = 0.0

    def roll_mode(self):
        self.modes = np.roll(self.modes, shift=-1)

    def reset_mode(self):
        self.modes = self.default_modes

    def current_mode(self):
        return self.modes[0]

    def mode_steering_throttle(self, user_steering, user_throttle, ai_steering, ai_throttle):
        if self.current_mode() == KeynoteDriver.MODE_USER:
            return user_steering, user_throttle
        elif self.current_mode() == KeynoteDriver.MODE_AI_STEERING:
            return ai_steering, user_throttle
        elif self.current_mode() == KeynoteDriver.MODE_AI:
            return ai_steering, ai_throttle
        else:
            return 0., 0.

    def initiate_emergency_stop(self):
        self.reset_mode()
        self.es_current_sequence = self.es_sequence

    def is_in_emergency_loop(self):
        return len(self.es_current_sequence) > 0

    def roll_emergency_stop(self):
        # TODO: change it !
        current_state = self.es_current_sequence.pop(0)
        if current_state == self.ES_START:
            return -1.0 * self.throttle_scale
        elif current_state == self.ES_THROTTLE_NEG_ONE:
            return 0.01
        elif current_state == self.ES_THROTTLE_POS_ONE:
            self.throttle = -1.0 * self.throttle_scale
            return self.throttle
        elif current_state == self.ES_THROTTLE_NEG_TWO:
            self.throttle += 0.05
            if self.throttle >= 0.0:
                self.throttle = 0.0
            return self.throttle

    def do_actions(self, actions):
        for action in actions:
            if action in self.actions_fn:
                self.actions_fn[action]()
            else:
                print("WARN: {} action does not exist.".format(action))

    def run(self, user_steering, user_throttle, user_actions, ai_steering, ai_throttle, ai_actions):
        if self.is_in_emergency_loop():
            return 0., self.roll_emergency_stop()
        else:
            self.do_actions(user_actions)
            self.do_actions(ai_actions)
            return self.mode_steering_throttle(user_steering, user_throttle, ai_steering, ai_throttle)
