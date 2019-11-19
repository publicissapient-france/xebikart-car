import tensorflow as tf

from donkeycar.parts.keras import KerasLinear


class OneOutputModel(KerasLinear):
    def run(self, *args):
        if len(args) == 1:
            inputs = tf.expand_dims(args[0], axis=0)
        else:
            inputs = [tf.expand_dims(arg, axis=0) for arg in args]
        prediction_outputs = self.model.predict(inputs)
        prediction_output = tf.squeeze(prediction_outputs, axis=0)
        prediction = prediction_output[0].numpy().item()
        return prediction


class PilotModel(KerasLinear):
    def run(self, img_arr):
        img_arr = tf.expand_dims(img_arr, axis=0)
        pilot_prediction = self.model.predict(img_arr)
        pilot_prediction = tf.squeeze(pilot_prediction, axis=0)
        steering = pilot_prediction[0].numpy().item()
        throttle = pilot_prediction[1].numpy().item()
        return steering, throttle
