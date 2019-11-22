import json
import time
import paho.mqtt.client as mqtt
import logging
import queue


class MQTTClient:

    def __init__(self, cfg, publish_delay=1):
        self.publish_delay = publish_delay

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.client.username_pw_set(username=cfg.RABBITMQ_USERNAME, password=cfg.RABBITMQ_PASSWORD)
        self.client.connect(cfg.RABBITMQ_HOST, cfg.RABBITMQ_PORT, 60)
        self.client.loop_start()
        self.client.subscribe(cfg.RABBITMQ_TOPIC + "/cars/" + str(cfg.CAR_ID))

        self.cfg = cfg
        self.running = True
        self.output_payload = None
        self.input_payload = None

        logging.debug("MQTT client initialized")

    def on_connect(self, mqttc, obj, flags, rc):
        logging.debug("Connected: " + str(rc))

    def on_message(self, mqttc, obj, msg):
        logging.debug("Message received: " + str(msg.payload))
        try:
            text_payload = msg.payload.decode("UTF-8")
            dict_payload = json.loads(text_payload)
            if 'mode' in dict_payload and 'car' in dict_payload and dict_payload['car'] == self.cfg.CAR_ID:
                self.input_payload['mode'] = dict_payload['mode']
        except Exception as e:
            logging.error("Error when processing message", e)

    def on_publish(self, mqttc, obj, result):
        logging.debug("Message published: " + str(result))

    def update(self):
        while self.running:
            if self.output_payload is not None:
                try:
                    self.client.publish(self.cfg.RABBITMQ_TOPIC, json.dumps(self.output_payload))
                    time.sleep(self.publish_delay)
                except Exception as e:
                    logging.error("Error when publishing message", e)

    def run_threaded(
            self,
            mode,
            user_angle, user_throttle,  # from controller
            location, borders  # from lidar
    ):
        self.output_payload = {
            'car': self.cfg.CAR_ID,
            'mode': mode,
            'user': {
                "angle": user_angle,
                "throttle": user_throttle
            },
            'position': {
                'x': location.x,
                'y': location.y
            },
            'angle': location.angle,
            'borders': borders
        }
        if self.input_payload is not None:
            return self.input_payload['mode']
        else:
            return None

    def shutdown(self):
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()


class MQTTSubscriber:
    def __init__(self, cfg, topic):
        self.topic = topic

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(username=cfg.RABBITMQ_USERNAME, password=cfg.RABBITMQ_PASSWORD)
        self.client.connect(cfg.RABBITMQ_HOST, cfg.RABBITMQ_PORT, 60)
        self.client.loop_start()
        self.client.subscribe(self.topic)

        self.cfg = cfg
        self.running = True
        self.input_queue = queue.Queue()

        logging.debug("MQTT client initialized")

    def on_connect(self, mqttc, obj, flags, rc):
        logging.debug("Connected: " + str(rc))

    def on_message(self, mqttc, obj, msg):
        logging.debug("Message received: " + str(msg.payload))
        text_payload = msg.payload.decode("UTF-8")
        dict_payload = json.loads(text_payload)
        self.input_queue.put_nowait(dict_payload)

    def run(self):
        raise NotImplementedError

    def shutdown(self):
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()


class MQTTPublisher:
    def __init__(self, cfg, topic, publish_delay=1):
        self.publish_delay = publish_delay
        self.topic = topic

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.username_pw_set(username=cfg.RABBITMQ_USERNAME, password=cfg.RABBITMQ_PASSWORD)
        self.client.connect(cfg.RABBITMQ_HOST, cfg.RABBITMQ_PORT, 60)
        self.client.loop_start()

        self.cfg = cfg
        self.running = True
        self.output_queue = queue.Queue()

        logging.debug("MQTT client initialized")

    def on_connect(self, mqttc, obj, flags, rc):
        logging.debug("Connected: " + str(rc))

    def on_publish(self, mqttc, obj, result):
        logging.debug("Message published: " + str(result))

    def update(self):
        while self.running:
            try:
                while not self.output_queue.empty():
                    msg = self.output_queue.get_nowait()
                    self.client.publish(self.topic, msg)
            except queue.Empty as e:
                pass
            time.sleep(self.publish_delay)

    def run_threaded(self, *args):
        raise NotImplementedError

    def shutdown(self):
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()


class RawMQTTPublisher(MQTTPublisher):
    def run_threaded(self, *args):
        self.output_queue.put_nowait(args[0])


class MetadataMQTTPublisher(MQTTPublisher):
    def __init__(self, car_id, *args, **kwargs):
        super(MetadataMQTTPublisher, self).__init__(*args, **kwargs)
        self.car_id = car_id

    def run_threaded(self, *args):
        (mode,
         # from controller
         user_angle, user_throttle,
         # from lidar
         location, borders) = args

        self.output_queue.put_nowait(json.dumps({
            'car': self.car_id,
            'mode': mode,
            'user': {
                "angle": user_angle,
                "throttle": user_throttle
            },
            'position': {
                'x': location.x,
                'y': location.y
            },
            'angle': location.angle,
            'borders': borders
        }))


class RemoteModeMQTTSubscriber(MQTTSubscriber):
    def __init__(self, car_id, *args, **kwargs):
        super(RemoteModeMQTTSubscriber, self).__init__(*args, **kwargs)
        self.car_id = car_id

    def run(self):
        mode = None

        while not self.input_queue.empty():
            dict_payload = self.input_queue.get_nowait()
            if ('mode' in dict_payload
                    and 'data' in dict_payload
                    and 'carId' in dict_payload['data']
                    and dict_payload['data']['carId'] == self.car_id):
                mode = dict_payload['mode']
        return mode
