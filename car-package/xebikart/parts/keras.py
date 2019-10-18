import tensorflow as tf

from donkeycar.parts.keras import KerasLinear


class OneOutputModel(KerasLinear):
    def run(self, img_arr):
        img_arr = tf.expand_dims(img_arr, axis=0)
        prediction_outputs = self.model.predict(img_arr)
        prediction_output = tf.squeeze(prediction_outputs, axis=0)
        prediction = prediction_output[0]
        return prediction


class PilotModel(KerasLinear):
    def run(self, img_arr):
        img_arr = tf.expand_dims(img_arr, axis=0)
        pilot_prediction = self.model.predict(img_arr)
        pilot_prediction = tf.squeeze(pilot_prediction, axis=0)
        steering = pilot_prediction[0]
        throttle = pilot_prediction[1]
        return steering, throttle
