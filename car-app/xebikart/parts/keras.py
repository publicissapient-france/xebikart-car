import tensorflow as tf

from donkeycar.parts.keras import KerasLinear


class KerasAngleModel(KerasLinear):
    def __init__(self, fix_throttle, *args, **kwargs):
        super(KerasAngleModel, self).__init__(*args, **kwargs)
        self.fix_throttle = fix_throttle

    def run(self, img_arr):
        img_arr = tf.expand_dims(img_arr, axis=0)
        img_prediction = self.model.predict(img_arr)
        img_prediction = tf.squeeze(img_prediction, axis=0)
        angle = img_prediction[0]
        return angle, self.fix_throttle
