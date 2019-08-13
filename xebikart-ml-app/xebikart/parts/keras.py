import tensorflow as tf


class KerasSimpleModel:
    def __init__(self, model_path):
        self.model = tf.keras.models.load_model(model_path)

    def run(self, img_arr):
        img_arr = tf.expand_dims(img_arr, axis=0)
        img_prediction = self.model.predict(img_arr)
        return tf.squeeze(img_prediction, axis=0)
