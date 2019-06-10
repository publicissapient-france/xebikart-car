from vae.controller import VAEController
from algos.custom_sac import SACWithVAE
import numpy as np


class SACModel:
    def __init__(self, vae_path, sac_path, n_command_history):
        # VAE
        self.vae = VAEController()
        self.vae.load(vae_path)
        # SAC Model
        self.sac = SACWithVAE.load(sac_path)
        # History
        self.n_command_history = 2 * n_command_history
        self.command_history = np.zeros((1, self.n_command_history))

    def run(self, img_arr):
        # appy vae and append history
        img_after_vae = self._apply_vae(img_arr)
        img_vae_history = self._add_history(img_after_vae)
        action, _ = self.sac.predict(img_vae_history)

        # Update command history
        self.command_history = np.roll(self.command_history, shift=-2, axis=-1)
        self.command_history[..., -2:] = action
        # print(len(outputs), outputs)
        steering = action[0]
        throttle = action[1]
        # outputs = [steering, throttle]
        return steering, throttle

    def _apply_vae(self, img_arr):
        return self.vae.encode(img_arr)

    def _add_history(self, img_after_vae):
        return np.concatenate((img_after_vae, self.command_history), axis=-1)