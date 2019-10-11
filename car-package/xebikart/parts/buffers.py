import numpy as np


class Sum:
    def __init__(self, buffer_size):
        self.buffer_size = buffer_size
        self.buffer = np.zeros(self.buffer_size)

    def run(self, input):
        self.buffer = np.roll(self.buffer, shift=-1, axis=-1)
        self.buffer[0] = input
        return np.sum(self.buffer)
