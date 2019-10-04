import numpy as np
import tensorflow as tf


class MemorySoftActorCriticModel(object):
    def __init__(self, checkpoint_path, n_command_history, min_throttle, max_throttle):
        # Model
        self.input_tensor = "main_level/agent/policy/online/network_0/observation/observation:0"
        self.output_tensor = "main_level/agent/policy/online/network_0/sac_policy_head_0/policy_mean:0"

        self.min_throttle = min_throttle
        self.max_throttle = max_throttle

        self.sess = tf.compat.v1.Session()
        saver = tf.compat.v1.train.import_meta_graph(checkpoint_path + ".meta")
        saver.restore(self.sess, checkpoint_path)

        # History
        self.n_command_history = 2 * n_command_history
        self.command_history = np.zeros(self.n_command_history)

    def run(self, img_arr):
        # append history
        img_history = np.concatenate((img_arr, self.command_history), axis=-1)
        img_history = np.expand_dims(img_history, axis=0)
        actions = self.sess.run(self.output_tensor, {self.input_tensor: img_history})
        action = np.squeeze(actions, axis=0)

        # Update command history
        self.command_history = np.roll(self.command_history, shift=-2, axis=-1)
        self.command_history[..., -2:] = action

        # outputs = [steering, throttle]
        steering = action[0]
        # Convert from [-1, 1] to [0, 1]
        ref_throttle = (action[1] + 1) / 2
        # Convert from [0, 1] to [min, max]
        throttle = ((1 - ref_throttle) * self.min_throttle) + (self.max_throttle * ref_throttle)
        return steering, throttle

