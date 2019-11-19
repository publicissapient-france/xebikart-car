import time
import tensorflow as tf
import numpy as np

from xebikart.lite_functions import interpreter_and_details


class TFLiteModel(object):
    def __init__(self, model_path):
        self.model = None

        # Load TFLite model and allocate tensors.
        self.interpreter, self.input_details, self.output_details = interpreter_and_details(model_path)

    def _infer(self, *args):
        if len(args) == 1:
            inputs = tf.expand_dims(args[0], axis=0)
        else:
            inputs = [tf.expand_dims(arg, axis=0) for arg in args]
        self.interpreter.set_tensor(self.input_details[0]['index'], inputs)
        self.interpreter.invoke()

        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        output_data = tf.squeeze(output_data, axis=0)
        return output_data

    def run(self, img_arr):
        return self._infer(img_arr)


class AsyncTFLiteModel(TFLiteModel):
    def __init__(self, rate_hz, **kwargs):
        super(AsyncTFLiteModel, self).__init__(**kwargs)
        self.rate_hz = rate_hz
        self.last_prediction = 0.
        self.new_img_arr = None
        self.on = True

    def update(self):
        while self.on:
            start_time = time.time()

            if self.new_img_arr is not None:
                self.last_prediction = self.run(self.new_img_arr)
                self.new_img_arr = None

            sleep_time = 1.0 / self.rate_hz - (time.time() - start_time)
            if sleep_time > 0.:
                time.sleep(sleep_time)

    def run_threaded(self, img_arr):
        self.new_img_arr = img_arr
        return self.last_prediction

    def shutdown(self):
        self.on = False


class AsyncBufferedAction(AsyncTFLiteModel):
    def __init__(self, buffer_size, *args, **kwargs):
        super(AsyncBufferedAction, self).__init__(*args, **kwargs)
        self.buffer = np.zeros(buffer_size)

    def _infer(self, img_arr):
        prediction = super(AsyncBufferedAction, self)._infer(img_arr)
        self.buffer = np.roll(self.buffer, shift=-1, axis=-1)
        self.buffer[0] = prediction
        return self.buffer
