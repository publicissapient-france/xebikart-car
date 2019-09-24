import json

import config


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
