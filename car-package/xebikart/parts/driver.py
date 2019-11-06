import numpy as np

from abc import ABC, abstractmethod


class Driver:

    def __init__(self, config):
        self.config = config

    def run(
            self,
            mode,
            user_angle, user_throttle,  # from controller
            pilot_angle, pilot_throttle,  # from ML model
            x, y, z, angle,  # from lidar
            dx, dy, dz, tx, ty, tz  # from imu
    ):
        if mode == 'user':
            return user_angle, user_throttle, True, self.config.IMU_ENABLED, self.config.LIDAR_ENABLED
        else:
            return pilot_angle, pilot_throttle, False, self.config.IMU_ENABLED, self.config.LIDAR_ENABLED


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
    EMERGENCY_STOP = "emergency_stop"
    MODE_TOGGLE = "mode_toggle"
    EXIT_SAFE_MODE = "exit_safe_mode"
    INCREASE_THROTTLE = "increase_throttle"
    DECREASE_THROTTLE = "decrease_throttle"

    def __init__(self):
        self.current_mode = UserMode()

    def run(self, user_steering, user_throttle, user_actions, ai_steering, detect_box, exit_buffer, brightness_buffer):

        steering, throttle = self.current_mode.run(user_steering, user_throttle, user_actions,
                                                   ai_steering, detect_box, exit_buffer, brightness_buffer)
        self.current_mode = self.current_mode.next_mode
        return steering, throttle


class Mode(ABC):
    def __init__(self):
        self.js_actions_fn = {}
        self.next_mode = self

    def do_js_actions(self, actions):
        for action in actions:
            if action in self.js_actions_fn:
                self.js_actions_fn[action]()
            else:
                print("WARN: {} action does not exist.".format(action))

    def set_next_mode(self, next_mode):
        self.next_mode = next_mode

    def fn_set_next_mode(self, next_mode):
        return lambda: self.set_next_mode(next_mode)

    @abstractmethod
    def run(self, user_steering, user_throttle, user_actions, ai_steering, detect_box, exit_buffer, brightness_buffer):
        raise NotImplemented


class SafeMode(Mode):
    def __init__(self):
        super(SafeMode, self).__init__()
        self.js_actions_fn = {
            KeynoteDriver.EXIT_SAFE_MODE: self.fn_set_next_mode(UserMode())
        }

    def run(self, user_steering, user_throttle, user_actions, ai_steering, detect_box, exit_buffer, brightness_buffer):
        self.do_js_actions(user_actions)
        return user_steering, user_throttle


class EmergencyStopMode(Mode):
    ES_START = 1
    ES_THROTTLE_NEG_ONE = 2
    ES_THROTTLE_POS_ONE = 3
    ES_THROTTLE_NEG_TWO = 4

    def __init__(self):
        super(EmergencyStopMode, self).__init__()
        # Emergency stop sequences
        self.es_sequence = [-0.4, 0.01, -0.4, 0., 0.,
                            0., 0., 0., 0., 0., 0., 0.]
        self.es_current_sequence = []

    def is_in_loop(self):
        return len(self.es_current_sequence) > 0

    def roll_emergency_stop(self):
        throttle = self.es_current_sequence.pop(0)
        return throttle

    def run(self, user_steering, user_throttle, user_actions, ai_steering, detect_box, exit_buffer, brightness_buffer):
        if self.is_in_loop():
            return 0., self.roll_emergency_stop()
        else:
            self.set_next_mode(SafeMode())
            return 0., 0.


class UserMode(Mode):
    def __init__(self):
        super(UserMode, self).__init__()
        self.js_actions_fn = {
            KeynoteDriver.EMERGENCY_STOP: self.fn_set_next_mode(EmergencyStopMode()),
            KeynoteDriver.MODE_TOGGLE: self.fn_set_next_mode(AISteeringMode())
        }

    def check_ai_buffers(self, detect_box, exit_buffer, brightness_buffer):
        if np.sum(detect_box) > 1. or np.sum(exit_buffer) > 1. or np.sum(brightness_buffer) < 500000.:
            self.set_next_mode(EmergencyStopMode())

    def run(self, user_steering, user_throttle, user_actions, ai_steering, detect_box, exit_buffer, brightness_buffer):
        self.do_js_actions(user_actions)
        self.check_ai_buffers(detect_box, exit_buffer, brightness_buffer)
        return user_steering, user_throttle


class AISteeringMode(Mode):
    def __init__(self):
        super(AISteeringMode, self).__init__()
        self.js_actions_fn = {
            KeynoteDriver.EMERGENCY_STOP: self.fn_set_next_mode(EmergencyStopMode()),
            KeynoteDriver.MODE_TOGGLE: self.fn_set_next_mode(AIMode())
        }

    def check_ai_buffers(self, detect_box, exit_buffer, brightness_buffer):
        if np.sum(detect_box) > 1. or np.sum(exit_buffer) > 1. or np.sum(brightness_buffer) < 500000.:
            self.set_next_mode(EmergencyStopMode())

    def run(self, user_steering, user_throttle, user_actions, ai_steering, detect_box, exit_buffer, brightness_buffer):
        self.do_js_actions(user_actions)
        self.check_ai_buffers(detect_box, exit_buffer, brightness_buffer)
        return ai_steering, user_throttle


class AIMode(Mode):
    def __init__(self):
        super(AIMode, self).__init__()
        self.js_actions_fn = {
            KeynoteDriver.EMERGENCY_STOP: self.fn_set_next_mode(EmergencyStopMode()),
            KeynoteDriver.MODE_TOGGLE: self.fn_set_next_mode(UserMode()),
            KeynoteDriver.INCREASE_THROTTLE: self.fn_throttle(0.1),
            KeynoteDriver.DECREASE_THROTTLE: self.fn_throttle(-0.1)
        }
        self.const_throttle = 0.2

    def fn_throttle(self, to_add):
        return lambda: self.const_throttle + to_add

    def check_ai_buffers(self, detect_box, exit_buffer, brightness_buffer):
        if np.sum(detect_box) > 1. or np.sum(exit_buffer) > 1. or np.sum(brightness_buffer) < 500000.:
            self.set_next_mode(EmergencyStopMode())

    def run(self, user_steering, user_throttle, user_actions, ai_steering, detect_box, exit_buffer, brightness_buffer):
        self.do_js_actions(user_actions)
        self.check_ai_buffers(detect_box, exit_buffer, brightness_buffer)
        return ai_steering, self.const_throttle
