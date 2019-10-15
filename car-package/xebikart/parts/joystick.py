from donkeypart_ps3_controller import PS3JoystickController
from xebikart.parts.driver import KeynoteDriver


class KeynoteJoystick(PS3JoystickController):

    def __init__(self, *args, **kwargs):
        super(KeynoteJoystick, self).__init__(*args, **kwargs)
        self.default_actions = {
            KeynoteDriver.EMERGENCY_STOP: False,
            KeynoteDriver.MODE_TOGGLE: False
        }
        self.actions = self.default_actions

    def init_js(self):
        super(KeynoteJoystick, self).init_js()
        if self.js is None:
            raise RuntimeError("Unable to start Joystick Controller")

    def init_trigger_maps(self):
        super(KeynoteJoystick, self).init_trigger_maps()

        self.button_down_trigger_map = {
            'cross': self.record_action(KeynoteDriver.EMERGENCY_STOP),
            'select': self.record_action(KeynoteDriver.MODE_TOGGLE)
        }

        self.button_up_trigger_map = {}

    def record_action(self, action):
        def _fn():
            self.actions[action] = True
        return _fn

    def run_threaded(self):
        actions = [k for k, v in self.actions if v is True]
        # reset actions
        self.actions = self.default_actions

        return self.angle, self.throttle, actions
