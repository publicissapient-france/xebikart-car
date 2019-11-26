import logging
import math
import time
from collections import deque
from operator import itemgetter

import serial
from rplidar import RPLidar as rpl
from xebikart.box import MinimumBoundingBox

ANGLE_SLOTS = 36
ANGLE_MAX = 360
ANGLE_HISTORY_LENGTH = 10


# These sample was extracted and adapted from donkeycar parts samples. Original version can be found here:
# https://github.com/autorope/donkeycar/blob/dev/donkeycar/parts/lidar.py
# donkeycar setup does not automatically include theses parts, not sure why yet...
class LidarScan(object):
    '''
    https://github.com/SkoltechRobotics/rplidar
    '''

    def __init__(self, min_len=ANGLE_SLOTS, port='/dev/ttyUSB0'):
        self.lidar = rpl(port)
        self.lidar.clear_input()
        self.scan = None
        self.on = True
        self.min_len = min_len
        time.sleep(1)

    def update(self):
        while self.on:
            scans = self.lidar.iter_scans(max_buf_meas=1000, min_len=self.min_len)
            try:
                for scan in scans:
                    self.scan = scan
            except serial.serialutil.SerialException:
                logging.error('serial.serialutil.SerialException from Lidar. common when shutting down.')

    def run_threaded(self):
        return self.scan

    def shutdown(self):
        self.on = False
        time.sleep(2)
        self.lidar.stop()
        self.lidar.stop_motor()
        self.lidar.disconnect()


class LidarPosition:

    def __init__(self, refresh_time_in_seconds=1):
        self.measures = []
        self.angle_history = deque([])
        self.position = (0, 0, 0)
        self.border_positions = []
        self.refresh_time_in_seconds = refresh_time_in_seconds
        self.on = True

    def choose_angle(self, corner_points, angle):
        xs = [int(x) for (x, y) in corner_points]
        ys = [int(y) for (x, y) in corner_points]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)

        if x_max - x_min > y_max - y_min:
            angles = (angle + 90) % 360, (angle + 270) % 360
        else:
            angles = (angle % 360), (angle + 180) % 360

        (angle1, angle2) = angles
        angle_delta_sum1 = 0
        angle_delta_sum2 = 0
        for previous_angle in self.angle_history:
            angle_delta_sum1 += abs((angle1 - previous_angle + 180) % 360 - 180)
            angle_delta_sum2 += abs((angle2 - previous_angle + 180) % 360 - 180)

        return angle1 if angle_delta_sum1 < angle_delta_sum2 else angle2

    def measures_to_positions(self):
        return [
            (
                int(distance * math.sin(math.radians(angle))),
                int(distance * math.cos(math.radians(angle)))
            ) for (angle, distance) in self.measures
        ]

    def rotate(self, point, angle):
        rotation_angle = math.radians(-angle)
        x, y = point
        rotated_x = int((math.cos(rotation_angle) * x) - (math.sin(rotation_angle) * y))
        rotated_y = int((math.sin(rotation_angle) * x) + (math.cos(rotation_angle) * y))
        return rotated_x, rotated_y

    def corner_points_to_position(self, corner_points):
        xs = [int(x) for (x, y) in corner_points]
        ys = [int(y) for (x, y) in corner_points]
        x_min = abs(min(xs))
        y_min = abs(min(ys))
        return (x_min, y_min)

    def update(self):
        while self.on:
            time.sleep(self.refresh_time_in_seconds)
            if len(self.measures) < 1:
                continue

            positions = self.measures_to_positions()

            bounding_box = MinimumBoundingBox(positions)
            bounding_box_angle = math.degrees(bounding_box.unit_vector_angle) % 360
            corner_points = [self.rotate(point, bounding_box_angle) for point in bounding_box.corner_points]
            angle = self.choose_angle(corner_points, bounding_box_angle)

            rotated_corner_points = [self.rotate(point, angle) for point in bounding_box.corner_points]
            position = self.corner_points_to_position(rotated_corner_points)

            self.border_positions = [[x, y] for (x, y) in positions]
            self.position = (angle, position[0], position[1])
            self.angle_history.append(angle)
            if len(self.angle_history) > ANGLE_HISTORY_LENGTH:
                self.angle_history.popleft()

    def run_threaded(self, scan):
        return self.run(scan)

    def run(self, scan):
        if scan is not None and len(scan) > 0:
            self.measures = list(map(lambda item: (item[1], item[2]), scan))
        return self.position, self.border_positions

    def shutdown(self):
        self.on = False


class LidarDistances:

    def run(self, scan):
        if scan is not None and len(scan) > 0:
            angles = [0] * ANGLE_SLOTS
            for measure in scan:
                index = int(measure[1] * ANGLE_SLOTS // ANGLE_MAX)
                angles[index] = max(angles[index], measure[2])
            return angles
        else:
            return []


class LidarDistancesVector(object):

    def run(self, scan):
        scan = scan.copy() if scan is not None else [(0., 0., 0.), (0., 1., 0.), (0., 2., 0.)]
        scan.sort(key=itemgetter(1))

        current_item = scan.pop(0)
        next_item = scan.pop(0)

        v_distances = []

        for i in range(360):
            if math.fabs(current_item[1] - i) > math.fabs(next_item[1] - i):
                current_item = next_item
                if len(scan) > 0:
                    next_item = scan.pop(0)
            v_distances.append(current_item[2])

        return v_distances
