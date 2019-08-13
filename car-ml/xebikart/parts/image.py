import tensorflow as tf

import xebikart.images.transformer as image_transformer


class Normalize:
    def run(self, img_arr):
        return image_transformer.normalize(img_arr)


class Crop:
    def __init__(self, left_margin=0, height_margin=40, width=160, height=80):
        self.crop_fn = image_transformer.generate_crop_fn(left_margin=left_margin,
                                                          height_margin=height_margin,
                                                          width=width,
                                                          height=height)

    def run(self, img_arr):
        return self.crop_fn(img_arr)


class Edges:
    def run(self, img_arr):
        return image_transformer.edges(img_arr)


class VAEEmbedding:
    def __init__(self, model_path):
        self.vae = tf.keras.models.load_model(model_path, compile=False)
        self.vae_encoder = self.vae.get_layer('encoder')

    def run(self, img_arr):
        img_arr = tf.expand_dims(img_arr, axis=0)
        img_embedded = self.vae_encoder.predict(img_arr)[2]
        return tf.squeeze(img_embedded, axis=0)
