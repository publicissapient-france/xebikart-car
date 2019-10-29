class HigherThan:
    def __init__(self, threshold):
        self.threshold = threshold

    def run(self, input):
        return input > self.threshold


class LessThan:
    def __init__(self, threshold):
        self.threshold = threshold

    def run(self, input):
        return input < self.threshold
