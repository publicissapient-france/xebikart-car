import tensorflow as tf


class SimpleTensorFlow:

    def __init__(self, model_path):
        self.model = tf.keras.models.load_model(model_path)

    @staticmethod
    def preprocess_image(image):
        image = tf.convert_to_tensor(image, dtype=tf.float32)
        image = tf.divide(image, 255.0)  # normalize to [0,1] range

        ## reshape input image
        image_reshape = tf.reshape(image, [1, 120, 160, 3])
        ## Extract edges (Sobel algorithme)
        image_edges = tf.image.sobel_edges(image_reshape)
        image_edges_reshape = tf.reshape(image_edges[:, :, :, 0], [120, 160, 2])
        ## Convert to black and white
        # image_edges_contrast = tf.where(image_edges_reshape > 0.3,
        #                      255*tf.ones_like(image_edges_reshape),
        #                      tf.zeros_like(image_edges_reshape))

        ## reshape output to (120,160,1)
        image = tf.reshape(image_edges_reshape[:, :, 0], (120, 160, 1))
        # label=np.asanyarray(label)
        return image

    def predict(self, img_arr):
        img_tensor = SimpleTensorFlow.preprocess_image(img_arr)
        steering = self.model.predict(img_tensor)
        return steering