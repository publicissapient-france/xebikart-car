import json

import config


class Driver:

    def __init__(self):
        self.emergency_stop = 0


    def run(
            self,
            mode,
            user_angle, user_throttle,  # from controller
            pilot_angle, pilot_throttle,  # from ML model
            x, y, z, angle,  # from lidar
            dx, dy, dz, tx, ty, tz,   # from imu
            obstacle_prediction # from obstacle model
    ):
        if mode == 'user':
            stop = False
            return user_angle, user_throttle, True, config.IMU_ENABLED, config.LIDAR_ENABLED, stop
        else:
            self.emergency_stop += obstacle_prediction
            stop = (self.emergency_stop > 10)
            return pilot_angle, pilot_throttle, False, config.IMU_ENABLED, config.LIDAR_ENABLED, stop
