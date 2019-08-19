import time
import logging

import config


# This sample was extracted and adapted from donkeycar parts samples. Original version can be found here:
# https://github.com/autorope/donkeycar/blob/dev/donkeycar/parts/imu.py
# donkeycar setup does not automatically include theses parts, not sure why yet...

class Mpu6050:

    def __init__(self, addr=0x68, poll_delay=0.0166):
        if config.IMU_ENABLED:
            from mpu6050 import mpu6050
            self.sensor = mpu6050(addr)
        self.accel = {'x': 0., 'y': 0., 'z': 0.}
        self.gyro = {'x': 0., 'y': 0., 'z': 0.}
        self.temp = 0.
        self.poll_delay = poll_delay
        self.on = True

    def update(self):
        while config.IMU_ENABLED and self.on:
            self.poll()
            time.sleep(self.poll_delay)

    def poll(self):
        try:
            self.accel, self.gyro, self.temp = self.sensor.get_all_data()
        except:
            logging.error('failed to read imu!!')

    def run_threaded(self):
        return (
            self.accel['x'],
            self.accel['y'],
            self.accel['z'],
            self.gyro['x'],
            self.gyro['y'],
            self.gyro['z'],
            self.temp
        )

    def run(self):
        self.poll()
        return (
            self.accel['x'],
            self.accel['y'],
            self.accel['z'],
            self.gyro['x'],
            self.gyro['y'],
            self.gyro['z'],
            self.temp
        )

    def shutdown(self):
        self.on = False
