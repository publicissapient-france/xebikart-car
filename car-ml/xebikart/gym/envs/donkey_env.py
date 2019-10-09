# Original author: Roma Sokolkov
# Edited by Antonin Raffin
import os
import math

import gym
import numpy as np
from gym import spaces

from xebikart.gym.core.donkey_proc import DonkeyUnityProcess
from xebikart.gym.core.donkey_sim import DonkeyUnitySimController
from xebikart.gym.utils import get_or_download_simulator
from xebikart.gym.envs import rewards


class DonkeyEnv(gym.Env):
    """
    Gym interface for DonkeyCar with support for using
    a VAE encoded observation instead of raw pixels if needed.

    :param level: (int) DonkeyEnv level
    :param frame_skip: (int) frame skip, also called action repeat
    :param min_throttle: (float)
    :param max_throttle: (float)
    :param min_steering: (float)
    :param max_steering: (float)
    :param max_cte_error: (float) Max cross track error before game over
    :param camera_shape: (int, int, int) Camera shape (height, width, channel)
    """

    metadata = {
        "render.modes": ["human", "rgb_array"],
    }

    def __init__(self, level=0, frame_skip=2, max_cte_error=3.0,
                 camera_shape=(120, 160, 3),
                 min_steering=-1, max_steering=1,
                 min_throttle=0.4, max_throttle=0.6,
                 reward_fn=None, headless=True):
        # Check for env variable
        exe_path = get_or_download_simulator(os.environ.get('DONKEY_SIM_HOME'))

        # TCP port for communicating with simulation
        port = int(os.environ.get('DONKEY_SIM_PORT', 9091))

        self.unity_process = None
        print("Starting DonkeyGym env")
        # Start Unity simulation subprocess if needed
        self.unity_process = DonkeyUnityProcess()
        self.unity_process.start(exe_path, headless=headless, port=port)

        # start simulation com
        self.viewer = DonkeyUnitySimController(level=level, port=port, camera_shape=camera_shape)

        # min/max steering/throttle
        self.min_throttle = min_throttle
        self.max_throttle = max_throttle
        self.min_steering = min_steering
        self.max_steering = max_steering

        # max_cte_error
        self.max_cte_error = max_cte_error

        # camera_shape
        self.camera_shape = camera_shape

        # reward function
        default_reward_fn = rewards.speed(
            min_throttle=min_throttle,
            max_throttle=max_throttle,
            base_reward_weight=1,
            throttle_reward_weight=0.1,
            crash_reward_weight=-10,
            crash_speed_reward_weight=-5
        )
        self.reward_fn = reward_fn if reward_fn is not None else default_reward_fn

        # steering + throttle, action space must be symmetric
        self.action_space = spaces.Box(low=np.array([-1, -1]),
                                       high=np.array([1, 1]),
                                       dtype=np.float32)

        self.observation_space = spaces.Box(low=0, high=255,
                                            shape=self.camera_shape, dtype=np.uint8)

        self.seed()
        # Frame Skipping
        self.frame_skip = frame_skip
        # wait until loaded
        self.viewer.wait_until_loaded()

    def is_game_over(self, info):
        """
        :return: (bool)
        """
        return info["hit"] or math.fabs(info["cte"]) > self.max_cte_error

    def info(self):
        return self.viewer.info()

    def step(self, action):
        """
        :param action: (np.ndarray)
        :return: (np.ndarray, float, bool, dict)
        """
        # action[0] is the steering angle
        # action[1] is the throttle

        # Convert from [-1, 1] to [0, 1]
        t = (action[1] + 1) / 2
        # Convert from [0, 1] to [min, max]
        action[1] = (1 - t) * self.min_throttle + self.max_throttle * t

        # Repeat action if using frame_skip
        for _ in range(self.frame_skip):
            self.viewer.take_action(action)
            observation = self.viewer.observe()
            info = self.info()
            done = self.is_game_over(info)
            reward = self.reward_fn(0, done, info)

        return observation, reward, done, info

    def reset(self):
        self.viewer.reset()
        observation = self.viewer.observe()
        return observation

    def render(self, mode='human'):
        """
        :param mode: (str)
        """
        if mode == 'rgb_array':
            return self.viewer.handler.original_image
        return None

    def close(self):
        if self.unity_process is not None:
            self.unity_process.quit()
        self.viewer.close_connection()
        self.viewer.quit()
