

def create_env(vae, level=4, frame_skip=2, max_cte_error=3.0,
               min_steering=-1, max_steering=1,
               min_throttle=0.1, max_throttle=0.3,
               max_steering_diff=0.15, n_history=10,
               headless=True, reward_fn=None):

    from xebikart.gym.envs.donkey_env import DonkeyEnv
    from xebikart.gym.envs.wrappers import CropObservationWrapper, ConvVariationalAutoEncoderObservationWrapper, \
        HistoryBasedWrapper, EdgingObservationWrapper

    # Create donkey env
    donkey_env = DonkeyEnv(
      level=level, frame_skip=frame_skip, max_cte_error=max_cte_error,
      min_steering=min_steering, max_steering=max_steering,
      min_throttle=min_throttle, max_throttle=max_throttle,
      headless=headless, reward_fn=reward_fn
    )

    # CropObservation
    crop_obs = CropObservationWrapper(donkey_env, 0, 40, 160, 80)
    # Edging
    edging_obs = EdgingObservationWrapper(crop_obs)
    # VAE
    vae_obs = ConvVariationalAutoEncoderObservationWrapper(edging_obs, vae)
    # History
    history_obs = HistoryBasedWrapper(vae_obs, n_command_history=n_history, max_steering_diff=max_steering_diff)

    return history_obs


def create_stack_obs_clipping_steering(vae, level=4, frame_skip=2, max_cte_error=3.0,
                                       min_steering=-1, max_steering=1,
                                       min_throttle=0.1, max_throttle=0.3,
                                       max_steering_diff=0.15, num_stack=4,
                                       headless=True, reward_fn=None):

    from xebikart.gym.envs.donkey_env import DonkeyEnv
    from xebikart.gym.envs.wrappers import CropObservationWrapper, ConvVariationalAutoEncoderObservationWrapper, \
        EdgingObservationWrapper, ClipSteeringBasedOnPrevious
    from xebikart.gym.envs.gym_wrappers import FrameStack

    # Create donkey env
    donkey_env = DonkeyEnv(
      level=level, frame_skip=frame_skip, max_cte_error=max_cte_error,
      min_steering=min_steering, max_steering=max_steering,
      min_throttle=min_throttle, max_throttle=max_throttle,
      headless=headless, reward_fn=reward_fn
    )

    # CropObservation
    crop_obs = CropObservationWrapper(donkey_env, 0, 40, 160, 80)
    # Edging
    edging_obs = EdgingObservationWrapper(crop_obs)
    # VAE
    vae_obs = ConvVariationalAutoEncoderObservationWrapper(edging_obs, vae)
    # Stack
    stack_obs = FrameStack(vae_obs, num_stack=num_stack)
    # Clip steering action
    clip_action = ClipSteeringBasedOnPrevious(stack_obs, max_steering_diff=max_steering_diff)

    return clip_action


def create_fix_throttle_env(vae=None, level=4, frame_skip=2, max_cte_error=3.0,
                            min_steering=-1, max_steering=1, throttle=0.2,
                            headless=True, reward_fn=None):

    from xebikart.gym.envs.donkey_env import DonkeyEnv
    from xebikart.gym.envs.wrappers import CropObservationWrapper, ConvVariationalAutoEncoderObservationWrapper, \
        EdgingObservationWrapper, FixThrottle

    # Create donkey env
    donkey_env = DonkeyEnv(
      level=level, frame_skip=frame_skip, max_cte_error=max_cte_error,
      min_steering=min_steering, max_steering=max_steering,
      min_throttle=throttle, max_throttle=throttle,
      headless=headless, reward_fn=reward_fn
    )

    # CropObservation
    crop_obs = CropObservationWrapper(donkey_env, 0, 40, 160, 80)
    # Edging
    edging_obs = EdgingObservationWrapper(crop_obs)
    if vae is not None:
        # VAE
        vae_obs = ConvVariationalAutoEncoderObservationWrapper(edging_obs, vae)
        # Fix throttle
        return FixThrottle(vae_obs)
    else:
        return FixThrottle(edging_obs)
