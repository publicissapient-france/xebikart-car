#!/usr/bin/env python3

import logging
from paho.mqtt.client import Client

import config


class Consumer:

    def __init__(self):
        self.client = Client("sample-subscriber")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.username_pw_set(username=config.RABBITMQ_USERNAME, password=config.RABBITMQ_PASSWORD)
        self.client.connect(config.RABBITMQ_HOST, config.RABBITMQ_PORT, 60)
        self.client.subscribe(config.RABBITMQ_TOPIC)

    def on_connect(self, client, userdata, flags, rc):
        logging.debug("Connected with result code " + str(rc))

    def on_message(self, client, userdata, msg):
        logging.info("Received: " + str(msg.payload.decode()))

    def on_subscribe(self, client, obj, mid, granted_qos):
        logging.debug("Subscribed: " + str(mid) + " " + str(granted_qos))


if __name__ == '__main__':
    logging.basicConfig(format=config.LOG_FORMAT, level=config.LOG_LEVEL, handlers=[logging.StreamHandler()])
    consumer = Consumer()
    consumer.client.loop_forever()
