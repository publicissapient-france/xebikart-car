import json
import time
import paho.mqtt.client as mqtt

import config


class MQTTClient:

    def __init__(self, publish_delay=1):
        self.publish_delay = publish_delay

        self.json_encoder = json.JSONEncoder()

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.client.username_pw_set(username=config.RABBITMQ_USERNAME, password=config.RABBITMQ_PASSWORD)
        self.client.connect(config.RABBITMQ_HOST, config.RABBITMQ_PORT, 60)
        self.client.loop_start()
        self.client.subscribe(config.RABBITMQ_TOPIC + "/cars/" + str(config.CAR_ID))

        self.running = True
        self.output_payload = None
        self.input_payload = None

        print("MQTT client initialized")

    def on_connect(self, mqttc, obj, flags, rc):
        print("Connected: " + str(rc))

    def on_message(self, mqttc, obj, msg):
        try:
            text_paylod = msg.payload.decode("UTF-8")
            dict_payload = json.loads(text_payload)
            if 'mode' in dict_payload and 'car' in dict_payload and dict_payload['car'] == config.CAR_ID:
                self.input_payload['mode'] = dict_payload['mode']
        except Exception as e:
            print("Error when receiving message", e)

    def on_publish(self, mqttc, obj, result):
        print("Published: " + str(result))

    def update(self):
        while self.running:
            if self.output_payload is not None:
                try:
                    self.client.publish(config.RABBITMQ_TOPIC, json.dumps(self.output_payload))
                    time.sleep(self.publish_delay)
                except Exception as e:
                    print("Error when publishing message", e)

    def run_threaded(
            self,
            mode,
            user_angle, user_throttle,  # from controller
            x, y, z, angle,  # from lidar
            dx, dy, dz, tx, ty, tz  # from imu
    ):
        self.output_payload = {
            'car': config.CAR_ID,
            'mode': mode,
            'user': {
                "angle": user_angle,
                "throttle": user_throttle
            },
            'position': {
                'x': x,
                'y': y,
                'z': z
            },
            'angle': angle,
            'acceleration': {
                'x': dx,
                'y': dy,
                'z': dz
            },
            'angular_speed': {
                'x': tx,
                'y': ty,
                'z': tz
            }
        }
        if self.input_payload is not None:
            return self.input_payload['mode']
        else:
            return None

    def shutdown(self):
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()
