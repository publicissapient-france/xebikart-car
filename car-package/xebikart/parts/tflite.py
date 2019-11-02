import time
import tensorflow as tf


class AsyncTFLiteModel(object):

    def __init__(self, model_path, rate_hz):
        self.model = None
        self.rate_hz = rate_hz
        self.last_prediction = 0.
        self.new_img_arr = None
        self.on = True

        # Load TFLite model and allocate tensors.
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        # Get input and output tensors.
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        # Get Input shape
        self.input_shape = self.input_details[0]['shape']

    def _infer(self, img_arr):
        self.interpreter.set_tensor(self.input_details[0]['index'], img_arr)
        self.interpreter.invoke()

        outputs = []
        for tensor in self.output_details:
            output_data = self.interpreter.get_tensor(tensor['index'])
            outputs.append(output_data[0][0])
        return outputs[0]

    def update(self):
        while self.on:
            start_time = time.time()

            if self.new_img_arr is not None:
                self.last_prediction = self._infer(self.new_img_arr)
                self.new_img_arr = None

            sleep_time = 1.0 / self.rate_hz - (time.time() - start_time)
            if sleep_time > 0.:
                time.sleep(sleep_time)

    def run_threaded(self, img_arr):
        self.new_img_arr = img_arr
        return self.last_prediction

    def shutdown(self):
        self.on = False
