import os

# PATHS
CAR_PATH = PACKAGE_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_PATH = os.path.join(CAR_PATH, 'data')
MODELS_PATH = os.path.join(CAR_PATH, 'models')
TUB_PATH = os.path.join(CAR_PATH, 'tub') # if using a single tub

# VEHICLE
DRIVE_LOOP_HZ = 20
MAX_LOOPS = 100000

# CAMERA (height, width)
CAMERA_RESOLUTION = (120, 160)
CAMERA_FRAMERATE = DRIVE_LOOP_HZ

# STEERING
STEERING_CHANNEL = 1
STEERING_LEFT_PWM = 550
STEERING_RIGHT_PWM = 250

# THROTTLE
THROTTLE_CHANNEL = 0
THROTTLE_FORWARD_PWM = 500
THROTTLE_STOPPED_PWM = 370
THROTTLE_REVERSE_PWM = 150

# TRAINING
BATCH_SIZE = 128
TRAIN_TEST_SPLIT = 0.8

# JOYSTICK
USE_JOYSTICK_AS_DEFAULT = True
JOYSTICK_MAX_THROTTLE = 0.25
JOYSTICK_STEERING_SCALE = 1.0
AUTO_RECORD_ON_THROTTLE = True
