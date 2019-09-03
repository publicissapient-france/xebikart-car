import tensorflow as tf

from donkeycar.parts.keras import KerasLinear


class SteeringModel(KerasLinear):
    def run(self, img_arr):
        img_arr = tf.expand_dims(img_arr, axis=0)
        steering_prediction = self.model.predict(img_arr)
        steering_prediction = tf.squeeze(steering_prediction, axis=0)
        steering = steering_prediction[0]
        return steering


class PilotModel(KerasLinear):
    def run(self, img_arr):
        img_arr = tf.expand_dims(img_arr, axis=0)
        pilot_prediction = self.model.predict(img_arr)
        pilot_prediction = tf.squeeze(pilot_prediction, axis=0)
        steering = pilot_prediction[0]
        throttle = pilot_prediction[1]
        return steering, throttle
