from donkeycar.parts.transform import Lambda


def add_publish_to_mqtt(vehicle, steering_input, throttle_input):
    from xebikart_app.parts.mqtt import MQTTClient

    mqtt_client = MQTTClient()
    vehicle.add(
        mqtt_client,
        inputs=[
            'user/mode',
            steering_input,
            throttle_input,
            'car/x',
            'car/y',
            'car/z',
            'car/angle',
            'car/dx',
            'car/dy',
            'car/dz',
            'car/tx',
            'car/ty',
            'car/tz'
        ],
        outputs=[
            'remote/mode'
        ],
        threaded=True
    )


def add_sensors(vehicle, cfg):
    from xebikart_app.parts.lidar import RPLidar, BreezySLAM
    from xebikart_app.parts.imu import Mpu6050

    is_imu_enabled_lb = Lambda(lambda: cfg.IMU_ENABLED)
    vehicle.add(
        is_imu_enabled_lb,
        outputs=[
            'imu_enabled'
        ]
    )
    is_lidar_enabled_lb = Lambda(lambda: cfg.LIDAR_ENABLED)
    vehicle.add(
        is_lidar_enabled_lb,
        outputs=[
            'lidar_enabled'
        ]
    )

    imu = Mpu6050()
    vehicle.add(
        imu,
        outputs=[
            'car/dx',
            'car/dy',
            'car/dz',
            'car/tx',
            'car/ty',
            'car/tz'
        ],
        threaded=True,
        run_condition='imu_enabled'
    )
    lidar = RPLidar()
    vehicle.add(
        lidar,
        outputs=[
            'lidar/distances',
            'lidar/angles'
        ],
        threaded=True,
        run_condition='lidar_enabled'
    )
    breezy_slam = BreezySLAM()
    vehicle.add(
        breezy_slam,
        inputs=[
            'lidar/distances',
            'lidar/angles'
        ],
        outputs=[
            'car/x',
            'car/y',
            'car/z',
            'car/angle',
        ],
        run_condition='lidar_enabled'
    )


def add_controller(vehicle, cfg, user_steering_output, user_throttle_output, user_mode_output, recording_output):
    from donkeypart_ps3_controller import PS3JoystickController
    controller = PS3JoystickController(
        throttle_scale=cfg.JOYSTICK_MAX_THROTTLE,
        steering_scale=cfg.JOYSTICK_STEERING_SCALE,
        auto_record_on_throttle=cfg.AUTO_RECORD_ON_THROTTLE
    )
    vehicle.add(
        controller,
        outputs=[
            user_steering_output,
            user_throttle_output,
            user_mode_output,
            recording_output
        ],
        threaded=True
    )


def add_pilot(vehicle, mode_input,
              user_steering_input, user_throttle_input,
              ai_steering_input, ai_throttle_input,
              steering_output, throttle_output):

    def _pilot(mode, user_steering, user_throttle, ai_steering, ai_throttle):
        if mode == 'user':
            return user_steering, user_throttle
        elif mode == 'local_angle':
            return ai_steering, user_throttle
        elif mode == 'local':
            return ai_steering, ai_throttle
        else:
            return 0., 0.

    decision_lb = Lambda(_pilot)
    vehicle.add(
        decision_lb,
        inputs=[
            mode_input,
            user_steering_input,
            user_throttle_input,
            ai_steering_input,
            ai_throttle_input
        ],
        outputs=[
            steering_output,
            throttle_output
        ]
    )


def add_logger(vehicle, prefix, input):
    def _log(i):
        print(f"{prefix}: {i}")

    log_lb = Lambda(_log)
    vehicle.add(
        log_lb,
        inputs=[
            input
        ]
    )


def add_throttle(vehicle, cfg, throttle_input):
    from donkeycar.parts.actuator import PWMThrottle, PCA9685
    throttle = PWMThrottle(
        controller=PCA9685(cfg.THROTTLE_CHANNEL),
        max_pulse=cfg.THROTTLE_FORWARD_PWM,
        zero_pulse=cfg.THROTTLE_STOPPED_PWM,
        min_pulse=cfg.THROTTLE_REVERSE_PWM
    )
    vehicle.add(
        throttle,
        inputs=[
            throttle_input
        ]
    )


def add_steering(vehicle, cfg, steering_input):
    from donkeycar.parts.actuator import PCA9685, PWMSteering
    steering = PWMSteering(
        controller=PCA9685(cfg.STEERING_CHANNEL),
        left_pulse=cfg.STEERING_LEFT_PWM,
        right_pulse=cfg.STEERING_RIGHT_PWM
    )
    vehicle.add(
        steering,
        inputs=[
            steering_input
        ]
    )


def add_timestamp(vehicle):
    from donkeycar.parts.clock import Timestamp
    clock = Timestamp()
    vehicle.add(
        clock,
        outputs=[
            'timestamp'
        ]
    )


def add_pi_camera(vehicle, cfg, camera_output):
    from donkeycar.parts.camera import PiCamera

    camera = PiCamera(resolution=cfg.CAMERA_RESOLUTION)
    vehicle.add(
        camera,
        outputs=[
            camera_output
        ],
        threaded=True
    )
