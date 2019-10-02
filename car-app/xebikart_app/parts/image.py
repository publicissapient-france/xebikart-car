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
