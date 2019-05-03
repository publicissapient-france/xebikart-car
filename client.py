import paho.mqtt.client as mqtt
import config


# The callback for when the client receives a CONNACK response from the server.
def on_connect(cli, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    cli.subscribe("$SYS/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(cli, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
username = config.RABBITMQ_USERNAME
password = config.RABBITMQ_PASSWORD
host = config.RABBITMQ_HOST
port = config.RABBITMQ_PORT
topic = config.RABBITMQ_TOPIC
client.username_pw_set(username=username, password=password)
client.connect(host, port, 60)
client.subscribe(topic)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
