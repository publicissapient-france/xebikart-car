import tensorflow as tf
import numpy as np

from xebikart.rl.sac import CustomSAC


class SoftActorCriticalModel:
    def __init__(self, sac_path):
        # SoftActorCritical Model
        self.sac = CustomSAC.load(sac_path)

    def run(self, img_arr):
        action, _ = self.sac.predict(img_arr)

        # outputs = [steering, throttle]
        steering = action[0]
        throttle = action[1]
        return steering, throttle


class MemorySoftActorCriticalModel(SoftActorCriticalModel):
    def __init__(self, sac_path, n_command_history):
        super(MemorySoftActorCriticalModel, self).__init__(sac_path)
        # History
        self.n_command_history = 2 * n_command_history
        self.command_history = np.zeros((1, self.n_command_history))

    def run(self, img_arr):
        # append history
        img_history = self._add_history(img_arr)
        action, _ = self.sac.predict(img_history)

        # Update command history
        self.command_history = np.roll(self.command_history, shift=-2, axis=-1)
        self.command_history[..., -2:] = action

        # outputs = [steering, throttle]
        steering = action[0]
        throttle = action[1]
        return steering, throttle

    def _add_history(self, img_encoded):
        return np.concatenate((img_encoded, self.command_history), axis=-1)

