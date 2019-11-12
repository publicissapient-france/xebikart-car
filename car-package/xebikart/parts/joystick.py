from donkeypart_ps3_controller import PS3JoystickController
from xebikart.parts.driver import KeynoteDriver


class Joystick(PS3JoystickController):

    def __init__(self, *args, **kwargs):
        super(Joystick, self).__init__(*args, **kwargs)
        self.actions = {}

    def init_js(self):
        super(Joystick, self).init_js()
        if self.js is None:
            raise RuntimeError("Unable to start Joystick Controller")

    def init_trigger_maps(self):
        super(Joystick, self).init_trigger_maps()

        self.button_down_trigger_map = {}

        self.button_up_trigger_map = {}

    def add_trigger_action(self, button, action):
        self.button_down_trigger_map[button] = self.record_action(action)

    def record_action(self, action):
        def _fn():
            self.actions[action] = True
        return _fn

    def run_threaded(self):
        actions = self.actions.copy()
        # reset actions
        self.actions = {}

        return self.angle, self.throttle, actions


class KeynoteJoystick(Joystick):

    def __init__(self, *args, **kwargs):
        super(KeynoteJoystick, self).__init__(*args, **kwargs)
        self.add_trigger_action('cross', KeynoteDriver.TRIGGER_EMERGENCY_STOP)
        self.add_trigger_action('square', KeynoteDriver.TRIGGER_EXIT_SAFE_MODE)
        self.add_trigger_action('circle', KeynoteDriver.TRIGGER_RETURN_MODE)
        self.add_trigger_action('select', KeynoteDriver.MODE_TOGGLE)
