import numpy as np


class Rolling:
    def __init__(self, buffer_size):
        self.buffer_size = buffer_size
        self.buffer = np.zeros(self.buffer_size)

    def run(self, input):
        self.buffer = np.roll(self.buffer, shift=-1, axis=-1)
        self.buffer[0] = input
        return self.buffer

