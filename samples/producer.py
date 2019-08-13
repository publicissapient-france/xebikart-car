#!/usr/bin/env python3

import time
import logging
from paho.mqtt.client import Client

import config


class Producer:

    def __init__(self):
        self.client = Client("sample-producer")
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.username_pw_set(username=config.RABBITMQ_USERNAME, password=config.RABBITMQ_PASSWORD)
        self.client.connect(config.RABBITMQ_HOST, config.RABBITMQ_PORT, 60)

    def on_connect(self, cli, userdata, flags, rc):
        logging.debug("Connected: " + str(rc))

    def on_publish(self, mqttc, metadata, rc):
        logging.debug("Published: " + str(rc))


if __name__ == '__main__':
    logging.basicConfig(format=config.LOG_FORMAT, level=config.LOG_LEVEL, handlers=[logging.StreamHandler()])
    producer = Producer()
    rc = 0
    while rc == 0:
        rc = producer.client.loop()
        producer.client.publish(config.RABBITMQ_TOPIC, 'hello world')
        time.sleep(2)
