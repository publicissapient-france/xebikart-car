import json


class Driver:

    def run(self, mode, user_angle, user_throttle, pilot_angle, pilot_throttle):
        if mode == 'user':
            return user_angle, user_throttle, True
        else:
            return pilot_angle, pilot_throttle, False
