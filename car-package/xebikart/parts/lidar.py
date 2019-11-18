import math
import serial
import logging

import time
import numpy as np


# These samples were extracted and adapted from donkeycar parts samples. Original version can be found here:
# https://github.com/autorope/donkeycar/blob/dev/donkeycar/parts/lidar.py
# donkeycar setup does not automatically include theses parts, not sure why yet...

class LidarScan(object):
    '''
    https://github.com/SkoltechRobotics/rplidar
    '''

    def __init__(self, port='/dev/ttyUSB0'):
        from rplidar import RPLidar as RPModule
        self.lidar = RPModule(port)
        self.lidar.clear_input()
        time.sleep(1)
        self.scan = [(0., 0., 0.), (0., 1., 0.)]
        self.on = True

    def update(self):
        scans = self.lidar.iter_scans(1000)
        try:
            for scan in scans:
                self.scan = scan
        except serial.serialutil.SerialException:
            logging.error('serial.serialutil.SerialException from Lidar. common when shutting down.')

    def run_threaded(self):
        quality, angles, distances = [list(t) for t in zip(*self.scan)]

        min_angles = min(angles)
        angles_distances = np.array(list(zip(angles, distances)))

        # Reset buffer to min angles
        while angles_distances[0][0] != min_angles:
            angles_distances = np.roll(angles_distances, shift=-1, axis=0)

        angles_distances = list(angles_distances.tolist())

        current_item = angles_distances.pop(0)
        next_item = angles_distances.pop(0)
        v_distances = []

        for i in range(360):
            if math.fabs(current_item[0] - i) > math.fabs(next_item[0] - i):
                current_item = next_item
                if len(angles_distances) > 0:
                    next_item = angles_distances.pop(0)
                else:
                    next_item = (i, 0.)
            v_distances.append(current_item[1])

        return v_distances

    def shutdown(self):
        self.on = False
        time.sleep(2)
        self.lidar.stop()
        self.lidar.stop_motor()
        self.lidar.disconnect()
