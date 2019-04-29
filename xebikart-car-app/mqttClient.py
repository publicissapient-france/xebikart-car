import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


def on_publish(client, userdata, result):
    print(f"data published ${result} \n")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.username_pw_set(username="admin", password="admin")
client.connect("localhost", 1883, 60)


class MqttPublisher:
    # def __init__(self, *args, **kwargs):
    #     super(MQTT, self).__init__(*args, **kwargs)

    def run(self, throttle):
        rc = 0
        while rc == 0:
            rc = client.loop()
            client.publish("hello/world", {"msg": throttle})
        return throttle
