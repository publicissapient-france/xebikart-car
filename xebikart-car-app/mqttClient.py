import json
import time
import paho.mqtt.client as mqtt

import config

def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))


def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.payload))


def on_publish(mqttc, obj, result):
    print("mid: " + str(result))
    pass


class MqttPublisher:

    def __init__(self, publish_delay=1):
        self.publish_delay = publish_delay

        self.client = mqtt.Client()
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.on_publish = on_publish

        username = config.RABBITMQ_USERNAME
        password = config.RABBITMQ_PASSWORD

        host = config.RABBITMQ_HOST
        port = config.RABBITMQ_PORT

        self.topic = config.RABBITMQ_TOPIC

        self.client.username_pw_set(username=username, password=password)
        self.client.connect(host, port, 60)

        self.running = True
        self.throttle = None

        print("MQTT client initialized")


    def update(self):
        while self.running:
            if self.throttle is not None:
                print("Publish: " + str(self.throttle))
                self.client.publish(self.topic, json.JSONEncoder.encode(json.JSONEncoder(), {"throttle": self.throttle}))
            time.sleep(self.publish_delay)


    def run_threaded(self, throttle):
        self.throttle = throttle
        return self.throttle


    def shutdown(self):
        self.running = False
        self.client.disconnect()
        self.client.loop_stop()