import tensorflow as tf


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
    interpreter = tf.compat.v1.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    # Get input and output tensors
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    return interpreter, input_details, output_details


def keras_session_to_tflite(model, out_filename):
    inputs = model.inputs
    outputs = model.outputs
    with tf.keras.backend.get_session() as sess:
        converter = tf.lite.TFLiteConverter.from_session(sess, inputs, outputs)
        tflite_model = converter.convert()
        open(out_filename, "wb").write(tflite_model)


def predictor_builder(model_path):
    """
    get a predictor from a lite model
    :param model_path: lite model path
    :return: predictor : a function that take a tf image and make the prediction
    """
    interpreter, input_details, output_details = interpreter_and_details(model_path)

    def predictor(input_image):
        input_image = tf.expand_dims(input_image)

        interpreter.set_tensor(input_details[0]['index'], input_image)
        interpreter.invoke()

        # The function `get_tensor()` returns a copy of the tensor data.
        # Use `tensor()` in order to get a pointer to the tensor.
        output_data = interpreter.get_tensor(output_details[0]['index'])
        output_data = tf.squeeze(output_data)

        return output_data

    return predictor

