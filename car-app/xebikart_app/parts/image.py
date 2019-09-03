import tensorflow as tf


class ImageTransformation:
    def __init__(self, transformations_fn):
        self.transformations_fn = transformations_fn

    def run(self, img_arr):
        for transformation_fn in self.transformations_fn:
            img_arr = transformation_fn(img_arr)
        return img_arr


class VAEEmbedding:
    def __init__(self, model_path):
        self.vae = tf.keras.models.load_model(model_path, compile=False)
        self.vae_encoder = self.vae.get_layer('encoder')

    def run(self, img_arr):
        img_arr = tf.expand_dims(img_arr, axis=0)
        img_embedded = self.vae_encoder.predict(img_arr)[2]
        return tf.squeeze(img_embedded, axis=0)
