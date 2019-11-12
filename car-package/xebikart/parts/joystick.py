from donkeypart_ps3_controller import PS3JoystickController


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
        self.add_trigger_action('cross', KeynoteAction.TRIGGER_EMERGENCY_STOP)
        self.add_trigger_action('square', KeynoteAction.TRIGGER_EXIT_SAFE_MODE)
        self.add_trigger_action('circle', KeynoteAction.TRIGGER_RETURN_MODE)
        self.add_trigger_action('select', KeynoteAction.MODE_TOGGLE)
        self.add_trigger_action('R1', KeynoteAction.INCREASE_THROTTLE)
        self.add_trigger_action('L1', KeynoteAction.DECREASE_THROTTLE)


class KeynoteAction:
    TRIGGER_EMERGENCY_STOP = "emergency_stop"
    TRIGGER_EXIT_SAFE_MODE = "exit_safe_mode"
    TRIGGER_RETURN_MODE = "active_return_mode"
    MODE_TOGGLE = "mode_toggle"
    INCREASE_THROTTLE = "increase_throttle"
    DECREASE_THROTTLE = "decrease_throttle"
