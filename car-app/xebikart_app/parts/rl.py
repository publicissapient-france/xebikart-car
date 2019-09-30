import numpy as np
import tensorflow as tf


class MemorySoftActorCriticModel(object):
    def __init__(self, checkpoint_path, n_command_history):
        # Model
        self.input_tensor = "main_level/agent/policy/online/network_0/observation/observation:0"
        self.output_tensor = "main_level/agent/policy/online/network_0/sac_policy_head_0/policy_mean:0"

        tf.reset_default_graph()

        self.sess = tf.compat.v1.Session()
        saver = tf.compat.v1.train.import_meta_graph(checkpoint_path + ".meta")
        saver.restore(self.sess, checkpoint_path)

        # History
        self.n_command_history = 2 * n_command_history
        self.command_history = np.zeros((1, self.n_command_history))

    def run(self, img_arr):
        # append history
        img_history = np.concatenate((img_arr, self.command_history), axis=-1)
        img_history = tf.expand_dims(img_history, axis=0)
        actions = self.sess.run(self.sess.output_tensor, {self.sess.input_tensor: img_history})
        action = tf.squeeze(actions, axis=0)

        # Update command history
        self.command_history = np.roll(self.command_history, shift=-2, axis=-1)
        self.command_history[..., -2:] = action

        # outputs = [steering, throttle]
        steering = action[0]
        throttle = action[1]
        return steering, throttle

