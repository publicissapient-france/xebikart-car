from xebikart.images import detect


class ImageTransformation:
    def __init__(self, transformations_fn):
        self.transformations_fn = transformations_fn

    def run(self, img_arr):
        for transformation_fn in self.transformations_fn:
            img_arr = transformation_fn(img_arr)
        return img_arr


class TFSessImageTransformation:
    def __init__(self, input_shape, transformations_fn):
        import tensorflow as tf

        self.input = tf.compat.v1.placeholder(tf.float32, shape=input_shape)
        assert len(transformations_fn) > 0
        tf_image = self.input
        for transformation_fn in transformations_fn:
            tf_image = transformation_fn(tf_image)
        self.transformations_fn = transformations_fn
        self.sess = tf.compat.v1.Session()
        self.output = tf_image

    def run(self, img_arr):
        return self.sess.run(self.output, {self.input: img_arr})


class ExtractColorAreaInBox:
    def __init__(self, color_to_detect, epsilon, nb_pixel_min):
        self.color_to_detect = color_to_detect
        self.epsilon = epsilon
        self.nb_pixel_min = nb_pixel_min

    def run(self, img_arr):
        return detect.bounding_color_area_in_box(img_arr, self.color_to_detect, self.epsilon, self.nb_pixel_min)
