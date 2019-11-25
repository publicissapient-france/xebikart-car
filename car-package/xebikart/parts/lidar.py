import logging
import math
import time
from collections import deque
from operator import itemgetter

import serial
from rplidar import RPLidar as rpl
from xebikart.box import MinimumBoundingBox

ANGLES_SLOTS = 36
ANGLE_MAX = 360
ANGLES_NORTH_SLOT = 0  # index for northern angle
ANGLES_SOUTH_SLOT = ANGLES_SLOTS // 2  # shift in index to retrieve southern angle
ANGLES_EAST_SLOT = ANGLES_SLOTS // 4  # shift in index to retrieve eastern angle
ANGLES_WEST_SLOT = ANGLES_EAST_SLOT + ANGLES_SOUTH_SLOT  # shift in index to retrieve western angle

ANGLE_HISTORY_LENGTH = 10


# These samples were extracted and adapted from donkeycar parts samples. Original version can be found here:
# https://github.com/autorope/donkeycar/blob/dev/donkeycar/parts/lidar.py
# donkeycar setup does not automatically include theses parts, not sure why yet...
class LidarScan(object):
    '''
    https://github.com/SkoltechRobotics/rplidar
    '''

    def __init__(self, min_len=ANGLES_SLOTS, port='/dev/ttyUSB0'):
        self.lidar = rpl(port)
        self.lidar.clear_input()
        time.sleep(1)
        self.scan = None
        self.on = True
        self.min_len = min_len

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
    rotation_angle = math.radians(-angle)
    x, y = point
    rotated_x = (math.cos(rotation_angle) * x) - (math.sin(rotation_angle) * y)
    rotated_y = (math.sin(rotation_angle) * x) + (math.cos(rotation_angle) * y)
    return rotated_x, rotated_y


def corner_points_to_positions(corner_points):
    xs = [int(x) for (x, y) in corner_points]
    ys = [int(y) for (x, y) in corner_points]
    x_min = abs(min(xs))
    y_min = abs(min(ys))
    return (x_min, y_min)


def choose_orientation_angles(corner_points, angle):
    xs = [int(x) for (x, y) in corner_points]
    ys = [int(y) for (x, y) in corner_points]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    if x_max - x_min > y_max - y_min:
        return (angle + 90) % 360, (angle + 270) % 360
    else:
        return (angle % 360), (angle + 180) % 360


def choose_angle(angle_history, angles):
    (angle1, angle2) = angles
    d_angle1 = 0
    d_angle2 = 0
    for previous_angle in angle_history:
        d_angle1 += abs((angle1 - previous_angle + 180) % 360 - 180)
        d_angle2 += abs((angle2 - previous_angle + 180) % 360 - 180)
    return angle1 if d_angle1 < d_angle2 else angle2


class LidarPosition:

    def __init__(self):
        self.measures = []
        self.angle_history = deque([])
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
            bounding_box_angle = math.degrees(bounding_box.unit_vector_angle) % 360

            rotated_corner_points = [rotate(point, bounding_box_angle) for point in bounding_box.corner_points]
            angles = choose_orientation_angles(rotated_corner_points, bounding_box_angle)
            estimated_angle = choose_angle(self.angle_history, angles)
            self.angle_history.append(estimated_angle)

            oriented_corner_points = [rotate(point, estimated_angle) for point in bounding_box.corner_points]
            position = corner_points_to_positions(oriented_corner_points)

            self.location = Location(angle=estimated_angle, x=position[0], y=position[1])
            if len(self.angle_history) > ANGLE_HISTORY_LENGTH:
                self.angle_history.popleft()

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
        if scan is not None and len(scan) > 0:
            angles = [0] * ANGLES_SLOTS
            for measure in scan:
                index = int(measure[1] * ANGLES_SLOTS // ANGLE_MAX)
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
