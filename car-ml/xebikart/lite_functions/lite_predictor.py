import tensorflow as tf
from tensorflow.compat.v1 import lite


def interpreter_and_details(model_path) :
    """
    get the interpreter and some details of a lite model thank to the model path
    :param model_path:
    :return:
        - an interpreter corresponding to our model
        - input_details
        - output_details
        - input_shape
    """

    # Load TFLite model and allocate tensors
    interpreter = lite.Interpreter(model_path = model_path)
    interpreter.allocate_tensors()

    # Get input and output tensors
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    input_shape = input_details[0]['shape']

    return interpreter, input_details, output_details, input_shape


def predictor_builder(model_path, preprocess):
    """
    get a predictor from a lite model and the corresponding preprocess
    :param model_path: lite model path
    :param preprocess: function used to process the image
    :return: predictor : a function that take a tf image and make the prediction
    """
    interpreter, input_details, output_details, input_shape = interpreter_and_details(model_path)

    def predictor(input_image):
        input_image = preprocess(input_image)
        input_image = tf.reshape(input_image, (1, input_image.shape[0], input_image.shape[1], 1))

        interpreter.set_tensor(input_details[0]['index'], input_image)
        interpreter.invoke()

        # The function `get_tensor()` returns a copy of the tensor data.
        # Use `tensor()` in order to get a pointer to the tensor.
        output_data = interpreter.get_tensor(output_details[0]['index'])

        return output_data

    return predictor

