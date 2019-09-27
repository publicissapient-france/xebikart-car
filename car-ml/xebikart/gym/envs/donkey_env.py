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
                 min_throttle=0.4, max_throttle=0.6, headless=True):
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

        # reward parameters
        self.THROTTLE_REWARD_WEIGHT = 0.1
        # Negative reward for getting off the road
        self.REWARD_CRASH = -10
        # Penalize the agent even more when being fast
        self.CRASH_SPEED_WEIGHT = 5

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

    def close_connection(self):
        return self.viewer.close_connection()

    def exit_scene(self):
        self.viewer.handler.send_exit_scene()

    def observation(self, observation):
        return observation

    def is_game_over(self):
        """
        :return: (bool)
        """
        return self.viewer.has_hit() or math.fabs(self.viewer.cte()) > self.max_cte_error

    def donkey_reward(self, done):
        """
        Compute reward:
        - +1 life bonus for each step + throttle bonus
        - -10 crash penalty - penalty for large throttle during a crash

        :param done: (bool)
        :return: (float)
        """
        if done:
            # penalize the agent for getting off the road fast
            norm_throttle = (self.viewer.last_throttle() - self.min_throttle) / (self.max_throttle - self.min_throttle)
            return self.REWARD_CRASH - self.CRASH_SPEED_WEIGHT * norm_throttle
        # 1 per timesteps + throttle
        throttle_reward = self.THROTTLE_REWARD_WEIGHT * (self.viewer.last_throttle() / self.max_throttle)
        return 1 + throttle_reward

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
            done = self.is_game_over()
            reward = self.donkey_reward(done)
            info = {}

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
