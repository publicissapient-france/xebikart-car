import json

import config


class Driver:

    def __init__(self):
        self.emergency_stop_obstacle = 0
        self.emergency_stop_exit = 0

    def run(
            self,
            mode,
            user_angle, user_throttle,  # from controller
            pilot_angle, pilot_throttle,  # from ML model
            x, y, z, angle,  # from lidar
            dx, dy, dz, tx, ty, tz,   # from imu
            obstacle_prediction, exit_prediction  # from obstacle model
    ):
        if mode == 'user':
            stop_obstacle, stop_exit = False, False
            return user_angle, user_throttle, True, config.IMU_ENABLED, config.LIDAR_ENABLED, stop_obstacle, stop_exit
        else:
            self.emergency_stop_obstacle += obstacle_prediction
            self.emergency_stop_exit += exit_prediction

            stop_obstacle, stop_exit = (self.emergency_stop_obstacle > 10), (self.emergency_stop_exit > 10)

            return pilot_angle, pilot_throttle, False, config.IMU_ENABLED, \
                   config.LIDAR_ENABLED, stop_obstacle, stop_exit
