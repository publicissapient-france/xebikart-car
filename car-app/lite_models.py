import numpy as np
import tensorflow as tf

from xebikart.images import transformer as T
from tensorflow.compat.v1 import lite
#TODO:import tensorflow.compat.v1


def prepare_image_obstacle(image_path, resize_shape=(160, 160)):
    tf_image = T.read_image(image_path)
    tf_image = T.normalize(tf_image)
    tf_image = tf.image.resize(tf_image, resize_shape, method=2)
    tf_image = tf.reshape(tf_image, (1, resize_shape[0], resize_shape[1], 3))

    return tf_image


def interpreter_and_details(model_path):
    # Load TFLite model and allocate tensors

    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    # Get input and output tensors
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    input_shape = input_details[0]['shape']

    return interpreter, input_details, output_details, input_shape


def predictor_builder(model_path, preprocess):
    interpreter, input_details, output_details, input_shape = interpreter_and_details(model_path)

    def predictor(input_image):
        input_image = np.array(preprocess(input_image))

        interpreter.set_tensor(input_details[0]['index'], input_image)
        interpreter.invoke()

        # The function `get_tensor()` returns a copy of the tensor data.
        # Use `tensor()` in order to get a pointer to the tensor.
        output_data = interpreter.get_tensor(output_details[0]['index'])

        return output_data[0][0]

    return predictor

