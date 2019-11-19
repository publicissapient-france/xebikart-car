import time
import math
import serial
import logging
from collections import deque

import config
from box import MinimumBoundingBox
from rplidar import RPLidar as rpl

ANGLES_SLOTS = 36
ANGLE_MAX = 360
ANGLES_NORTH_SLOT = 0  # index for northern angle
ANGLES_SOUTH_SLOT = ANGLES_SLOTS // 2  # shift in index to retrieve southern angle
ANGLES_EAST_SLOT = ANGLES_SLOTS // 4  # shift in index to retrieve eastern angle
ANGLES_WEST_SLOT = ANGLES_EAST_SLOT + ANGLES_SOUTH_SLOT  # shift in index to retrieve western angle

LOCATION_HISTORY_LENGTH = 10

# These samples were extracted and adapted from donkeycar parts samples. Original version can be found here:
# https://github.com/autorope/donkeycar/blob/dev/donkeycar/parts/lidar.py
# donkeycar setup does not automatically include theses parts, not sure why yet...

class RPLidar(object):
    '''
    https://github.com/SkoltechRobotics/rplidar
    '''

    def __init__(self, port='/dev/ttyUSB0'):
        self.lidar = rpl(port)
        self.lidar.clear_input()
        time.sleep(1)
        self.scan = None
        self.on = True

    def update(self):
        while self.on:
            scans = self.lidar.iter_scans(max_buf_meas=1000, min_len=ANGLES_SLOTS)
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


class Location:

    def __init__(self, angle, x, y):
        self.angle = angle
        self.x = x
        self.y = y


class Measure:

    def __init__(self, angle, distance):
        self.angle = angle
        self.distance = distance


def measures_to_positions(measures):
    return [
        (
            int(measure.distance * math.sin(math.radians(measure.angle))),
            int(measure.distance * math.cos(math.radians(measure.angle)))
        ) for measure in measures
    ]


def rotate(point, angle):
    rotation_angle = -angle
    x, y = point
    rotated_x = (math.cos(rotation_angle) * x) - (math.sin(rotation_angle) * y)
    rotated_y = (math.sin(rotation_angle) * x) + (math.cos(rotation_angle) * y)
    return rotated_x, rotated_y


def corner_points_to_positions(corner_points):
    xs = [int(x) for (x, y) in corner_points]
    ys = [int(y) for (x, y) in corner_points]
    x_min = abs(min(xs))
    y_min = abs(min(ys))
    x_max = max(xs)
    y_max = max(ys)
    return (x_min, y_min), (x_max, y_max)


def next_location(location_history, positions, raw_angle):
    (position1, position2) = positions
    sum_for_position1 = 0
    sum_for_position2 = 0
    for previous_location in location_history:
        previous_position = (previous_location.x, previous_location.y)
        sum_for_position1 += distance(position1, previous_position)
        sum_for_position2 += distance(position2, previous_position)
    next_position = position1 if sum_for_position1 < sum_for_position2 else position2
    next_angle = int(math.degrees(raw_angle) % 360)
    return Location(next_angle, next_position[0], next_position[1])


def distance(p1, p2):
    (x1, y1) = p1
    (x2, y2) = p2
    return ((x1 - x2) ** 2) + ((y1 - y2) ** 2)


def discrete_measures(measures):
    angles = [0 for x in range(ANGLES_SLOTS)]
    for measure in measures:
        index = int(measure[1] * ANGLES_SLOTS // ANGLE_MAX)
        angles[index] = max(angles[index], measure[2])
    return angles


class LidarPosition:

    def __init__(self):
        self.measures = []
        self.location_history = deque([])
        self.location = Location(angle=0, x=0, y=0)
        self.border_positions = []
        self.on = True

    def update(self):
        while self.on:
            time.sleep(1)
            if len(self.measures) < 1:
                continue
            positions = measures_to_positions(self.measures)
            self.border_positions = [[x, y] for (x, y) in positions]
            bounding_box = MinimumBoundingBox(positions)
            bounding_box_angle = bounding_box.unit_vector_angle
            rotated_corner_points = [rotate(point, bounding_box_angle) for point in bounding_box.corner_points]
            positions = corner_points_to_positions(rotated_corner_points)
            self.location = next_location(self.location_history, positions, bounding_box_angle)
            self.location_history.append(self.location)
            if len(self.location_history) > LOCATION_HISTORY_LENGTH:
                self.location_history.popleft()

    def run_threaded(self, scan):
        return self.run(scan)

    def run(self, scan):
        if scan is not None and len(scan) > 0:
            self.measures = list(map(lambda item: Measure(item[1], item[2]), scan))
        return self.location, self.border_positions

    def shutdown(self):
        self.on = False


class LidarDistances:

    def run(self, scan):
        result = []
        if scan is not None and len(scan) > 0:
            result = discrete_measures(scan)
        return result

    def shutdown(self):
        self.on = False
