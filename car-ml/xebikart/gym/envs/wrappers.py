import numpy as np

from gym.core import Wrapper, ObservationWrapper
from gym.spaces import Box

import xebikart.images.transformer as images_transformer


class CropObservationWrapper(ObservationWrapper):
    def __init__(self, env, left_margin, top_margin, width, height):
        """
        Crop observation based on left_margin, top_margin, width and height

        :param env:
        :param left_margin:
        :param top_margin:
        :param width:
        :param height:
        """

        super(CropObservationWrapper, self).__init__(env)

        self.original_shape = self.env.observation_space.shape
        assert self.original_shape[:2] == (top_margin + height, left_margin + width)

        self.new_shape = (height, width) + self.original_shape[2:]
        self.left_margin = left_margin
        self.top_margin = top_margin
        self.width = width
        self.height = height

        self.observation_space = Box(low=0,
                                     high=255,
                                     dtype=self.env.observation_space.dtype,
                                     shape=self.new_shape)

    def observation(self, observation):
        # Crop Region of interest
        return observation[
               self.top_margin:(self.top_margin + self.height),
               self.left_margin:(self.left_margin + self.width)
        ]


class EdgingObservationWrapper(ObservationWrapper):
    def __init__(self, env):
        """
        Edging image with 3 channels using tensorflow sobel_edges.
        First, it reduces all channel in one using mean math operation.

        Then, it uses sobel_edges to returns a new images with 2 channels,
        one for vertical edges, and another one for horizontal edges

        :param env:
        """
        super(EdgingObservationWrapper, self).__init__(env)
        original_shape = self.env.observation_space.shape
        assert original_shape[2] == 3

        import tensorflow as tf
        self.sess = tf.Session()

        self.image_placeholder = tf.placeholder(tf.float32, shape=original_shape)
        tf_image = images_transformer.normalize(self.image_placeholder)
        self.tf_edging_image = images_transformer.edges(tf_image)

        self.observation_space = Box(low=0., high=1.,
                                     shape=original_shape[:-1] + (2, ),
                                     dtype=self.env.observation_space.dtype)

    def observation(self, observation):
        return self.sess.run(self.tf_edging_image, {self.image_placeholder: observation})


class ConvVariationalAutoEncoderObservationWrapper(ObservationWrapper):
    def __init__(self, env, vae):
        """
        Apply VAE (Variational Auto Encoder) on observation.
        Based on keras implementation

        :param env:
        :param vae: tensorflow.keras.model
        """
        super(ConvVariationalAutoEncoderObservationWrapper, self).__init__(env)

        self.vae = vae
        self.vae_input_shape = self.vae.input_shape[1:]
        z_size = self.vae.output_shape[1]

        original_shape = self.env.observation_space.shape

        assert original_shape == self.vae_input_shape

        self.observation_space = Box(low=np.finfo(np.float32).min,
                                     high=np.finfo(np.float32).max,
                                     shape=(z_size, ),
                                     dtype=np.float32)

    def observation(self, observation):
        normalize_obs = observation / 255.
        normalize_obs = np.expand_dims(normalize_obs, 0)
        return self.vae.predict(normalize_obs)


class HistoryBasedWrapper(Wrapper):
    def __init__(self, env, n_command_history, max_steering_diff):
        """
        Add historical actions to observation and apply a penalty in case of "jerk move".
        A "jerk move" is consider each time two consecutive steering diff is higher than max_steering_diff.

        :param env:
        :param n_command_history:
        """
        super(HistoryBasedWrapper, self).__init__(env)

        assert len(self.env.observation_space.shape) == 1, "observation_space cannot have a multidimensional shape"
        assert self.env.observation_space.dtype == np.float32
        assert n_command_history > 1, "n_command_history at least 1"

        original_shape = self.env.observation_space.shape[0]

        # Save last n commands (throttle + steering)
        self.n_commands = self.env.action_space.shape[0]
        self.n_command_history = n_command_history
        # shape (1, x) to keep same as observation
        self.command_history = np.zeros((self.n_commands * self.n_command_history))

        # Max steering diff
        self.max_steering_diff = max_steering_diff

        # z latent vector from the VAE (encoded input image)
        self.observation_space = Box(low=np.finfo(np.float32).min,
                                     high=np.finfo(np.float32).max,
                                     shape=(original_shape + self.n_commands * self.n_command_history,),
                                     dtype=self.env.observation_space.dtype)

    def reset(self, **kwargs):
        self.command_history = np.zeros((self.n_commands * self.n_command_history))
        observation = self.env.reset(**kwargs)
        return self.observation(observation)

    def step(self, action):
        action = self.action(action)
        observation, reward, done, info = self.env.step(action)
        return self.observation(observation), reward, done, info

    def action(self, action):
        # Clip steering angle rate to enforce continuity
        prev_steering = self.command_history[-2]
        # Add an extra at clipping to penalty in case of bad decision
        # Take a look at reward function
        max_diff = self.max_steering_diff + 1e-5
        diff = np.clip(action[0] - prev_steering, -max_diff, max_diff)
        action[0] = prev_steering + diff

        # Update command history
        self.command_history = np.roll(self.command_history, shift=-self.n_commands)
        self.command_history[-self.n_commands:] = action
        return action

    def observation(self, observation):
        command_history_reshaped = np.reshape(self.command_history, (1, self.n_commands * self.n_command_history))
        command_history_reshaped = np.concatenate((observation, command_history_reshaped), axis=-1)
        return np.squeeze(command_history_reshaped)
