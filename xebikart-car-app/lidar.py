import time
import math
import serial


# These samples were extracted and adapted from donkeycar parts samples. Original version can be found here:
# https://github.com/autorope/donkeycar/blob/dev/donkeycar/parts/lidar.py
# donkeycar setup does not automatically include theses parts, not sure why yet...

class RPLidar(object):
    '''
    https://github.com/SkoltechRobotics/rplidar
    '''

    def __init__(self, port='/dev/ttyUSB0'):
        from rplidar import RPLidar
        self.port = port
        self.distances = []
        self.angles = []
        self.lidar = RPLidar(self.port)
        self.lidar.clear_input()
        time.sleep(1)
        self.on = True

    def update(self):
        scans = self.lidar.iter_scans(1000)
        while self.on:
            try:
                for scan in scans:
                    self.distances = [item[2] for item in scan]
                    self.angles = [item[1] for item in scan]
            except serial.serialutil.SerialException:
                print('serial.serialutil.SerialException from Lidar. common when shutting down.')

    def run_threaded(self):
        return self.distances, self.angles

    def shutdown(self):
        self.on = False
        time.sleep(2)
        self.lidar.stop()
        self.lidar.stop_motor()
        self.lidar.disconnect()


class BreezySLAM(object):
    '''
    https://github.com/simondlevy/BreezySLAM
    '''

    def __init__(self, map_size_pixels=500, map_size_meters=10, map_quality=5):
        from breezyslam.algorithms import RMHC_SLAM
        from breezyslam.sensors import Laser

        laser_model = Laser(
            scan_size=360,
            scan_rate_hz=10.,
            detection_angle_degrees=360,
            distance_no_detection_mm=12000
        )
        self.slam = RMHC_SLAM(
            laser_model,
            map_size_pixels,
            map_size_meters,
            map_quality
        )

    def run(self, distances, angles):
        self.slam.update(distances, scan_angles_degrees=angles)
        x, y, angle = self.slam.getpos()
        return x, y, (angle % 360)

    def shutdown(self):
        pass
