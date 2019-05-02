import json
import paho.mqtt.client as mqtt
import config


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {str(rc)}")


def on_message(client, userdata, msg):
    print(f"{msg.topic} {str(msg.payload)}")


def on_publish(client, userdata, result):
    print(f"data published {result} \n")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
username = config.RABBITMQ_USERNAME
password = config.RABBITMQ_PASSWORD
url = config.RABBITMQ_URL
port = config.RABBITMQ_PORT
topic = config.RABBITMQ_TOPIC
client.username_pw_set(username=username, password=password)
client.connect(url, port, 60)


class MqttPublisher:
    def run(self, throttle):
        client.publish(topic, json.JSONEncoder.encode(json.JSONEncoder(), {"throttle": throttle}))
        return throttle
