from donkeypart_ps3_controller import PS3JoystickController


class Joystick(PS3JoystickController):
    CROSS = "cross"
    CIRCLE = "circle"
    SQUARE = "square"
    SELECT = "select"
    R1 = "R1"
    L1 = "L1"

    def __init__(self, *args, **kwargs):
        super(Joystick, self).__init__(*args, **kwargs)
        self.button_triggered = {}

    def init_js(self):
        super(Joystick, self).init_js()
        if self.js is None:
            raise RuntimeError("Unable to start Joystick Controller")

    def init_trigger_maps(self):
        super(Joystick, self).init_trigger_maps()

        self.button_down_trigger_map = {}

        self.button_up_trigger_map = {
            button: self.record_button(button)
            for button in [Joystick.CROSS, Joystick.CIRCLE, Joystick.SQUARE, Joystick.SELECT, Joystick.R1, Joystick.L1]
        }

    def record_button(self, key):
        def _fn():
            self.button_triggered[key] = True
        return _fn

    def run_threaded(self):
        button_triggered = self.button_triggered.copy()
        # reset button_triggered
        self.button_triggered = {}

        return self.angle, self.throttle, button_triggered
