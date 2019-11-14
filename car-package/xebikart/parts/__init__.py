from donkeycar.parts.transform import Lambda


def add_mqtt_image_base64_publisher(vehicle, cfg, topic, camera_input):
    from xebikart.parts.mqtt import RawMQTTPublisher
    from xebikart.parts.image import EncodeToBase64

    encoder = EncodeToBase64()
    publisher = RawMQTTPublisher(cfg=cfg, topic=topic)
    vehicle.add(encoder, inputs=[camera_input], outputs=["encoder/base64"])
    vehicle.add(publisher, inputs=["encoder/base64"], threaded=True)


def add_mqtt_metadata_publisher(vehicle, cfg, topic, car_id,
                                steering="user/angle", throttle="user/throttle", mode="user/mode",
                                car_x="car/x", car_y="car/y", car_z="car/z", car_angle="car/angle",
                                car_dx="car/dx", car_dy="car/dy", car_dz="car/dz",
                                car_tx="car/tx", car_ty="car/ty", car_tz="car/tz",
                                ):
    from xebikart.parts.mqtt import MetadataMQTTPublisher

    mqtt_client = MetadataMQTTPublisher(car_id, cfg=cfg, topic=topic)
    vehicle.add(
        mqtt_client,
        inputs=[
            mode, steering, throttle,
            car_x, car_y, car_z, car_angle,
            car_dx, car_dy, car_dz,
            car_tx, car_ty, car_tz
        ],
        threaded=True
    )


def add_mqtt_remote_mode_subscriber(vehicle, cfg, topic, car_id, remote_mode):
    from xebikart.parts.mqtt import RemoteModeMQTTSubscriber

    mqtt_client = RemoteModeMQTTSubscriber(car_id, cfg=cfg, topic=topic)
    vehicle.add(mqtt_client, outputs=[remote_mode])


def add_imu_sensor(vehicle, cfg,
                   car_dx="car/dx", car_dy="car/dy", car_dz="car/dz",
                   car_tx="car/tx", car_ty="car/ty", car_tz="car/tz"):
    from xebikart.parts.imu import Mpu6050

    imu = Mpu6050()
    vehicle.add(
        imu,
        outputs=[
            car_dx,
            car_dy,
            car_dz,
            car_tx,
            car_ty,
            car_tz
        ],
        threaded=True,
    )


def add_lidar_sensor(vehicle, cfg, car_x="car/x", car_y="car/y", car_z="car/z", car_angle="car/angle"):
    from xebikart.parts.lidar import RPLidar, BreezySLAM

    lidar = RPLidar()
    vehicle.add(
        lidar,
        outputs=[
            'lidar/_distances',
            'lidar/_angles'
        ],
        threaded=True
    )
    breezy_slam = BreezySLAM()
    vehicle.add(
        breezy_slam,
        inputs=[
            'lidar/_distances',
            'lidar/_angles'
        ],
        outputs=[
            car_x,
            car_y,
            car_z,
            car_angle
        ]
    )


def add_logger(vehicle, prefix, input):
    def _log(i):
        print(prefix, ": ", i)

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


def add_brightness_detector(vehicle, buffer_size, camera_input, brightness_output):
    from xebikart.parts.image import ImageTransformation
    from xebikart.parts.buffers import Rolling
    import tensorflow as tf

    image_transformation = ImageTransformation([
        lambda x: tf.dtypes.cast(x, "int32"),
        tf.math.reduce_sum
    ])
    vehicle.add(image_transformation, inputs=[camera_input], outputs=['brightness/_reduce'])
    # Rolling buffer n last predictions
    buffer = Rolling(buffer_size=buffer_size)
    vehicle.add(buffer, inputs=['brightness/_reduce'], outputs=[brightness_output])


def add_color_box_detector(vehicle, color_to_detect, epsilon, nb_pixel_min, camera_input, detect_model_output):
    from xebikart.parts.image import ExtractColorAreaInBox

    # Get color box from image
    detection_model = ExtractColorAreaInBox(color_to_detect=color_to_detect, epsilon=epsilon, nb_pixel_min=nb_pixel_min)
    vehicle.add(detection_model, inputs=[camera_input], outputs=[detect_model_output])