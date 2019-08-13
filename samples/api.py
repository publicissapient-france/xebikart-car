#!/usr/bin/env python3

import time
import logging

from flask import Flask, Response
from paho.mqtt.client import Client

import config


class Subscriber():

    def __init__(self):
        self.messages = []
        self.client = Client("sample-api-subscriber")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.username_pw_set(username=config.RABBITMQ_USERNAME, password=config.RABBITMQ_PASSWORD)
        self.client.connect(config.RABBITMQ_HOST, config.RABBITMQ_PORT, 60)
        self.client.subscribe(config.RABBITMQ_TOPIC)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        logging.debug("Connected with result code " + str(rc))

    def on_message(self, cli, userdata, msg):
        logging.debug(msg.topic + " " + str(msg.payload.decode()))
        self.messages.append(str(msg.payload.decode()))

    def on_subscribe(self, client, obj, mid, granted_qos):
        logging.debug("Subscribed: " + str(mid) + " " + str(granted_qos))


if __name__ == "__main__":
    logging.basicConfig(format=config.LOG_FORMAT, level=config.LOG_LEVEL, handlers=[logging.StreamHandler()])

    subscriber = Subscriber()
    app = Flask(__name__)


    @app.route('/events')
    def get():
        def eventStream():
            while True:
                if (len(subscriber.messages) > 0):
                    yield "data: " + subscriber.messages.pop() + "\n"

        return Response(eventStream(), mimetype="text/event-stream")


    app.run()
