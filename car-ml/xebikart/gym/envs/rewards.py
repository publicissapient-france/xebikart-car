

def speed(min_throttle, max_throttle,
          base_reward_weight, throttle_reward_weight,
          crash_reward_weight, crash_speed_reward_weight):
    """
    default: [base_reward_weight] + [throttle_reward_weight]
    done: [crash_reward_weight] + [crash_speed_reward_weight] * [current_throttle] during a crash

    :param min_throttle:
    :param max_throttle:
    :param base_reward_weight:
    :param throttle_reward_weight:
    :param crash_reward_weight:
    :param crash_speed_reward_weight:
    :return:
    """
    def _reward_fn(reward, done, info):
        if done:
            # penalize the agent for getting off the road fast
            throttle = info["throttle"]
            norm_throttle = (throttle - min_throttle) / (max_throttle - min_throttle)
            return crash_reward_weight + crash_speed_reward_weight * norm_throttle
        else:
            # step_reward + throttle_reward
            throttle = info["throttle"]
            ref_throttle = (throttle / max_throttle)
            throttle_reward = throttle_reward_weight * ref_throttle
            return base_reward_weight + throttle_reward
    return _reward_fn


def smooth_driving(max_steering_diff, steering_diff_reward_weight):
    """
    diff between prev_steering - steering > max_steering_diff: steering_diff_reward_weight * (1 + error ** 2)
    default: default reward

    :param max_steering_diff:
    :param steering_diff_reward_weight:
    :return:
    """

    # hack way to keep last info in memory
    class _Memory:
        info = {
            "throttle": 0.,
            "steering": 0.
        }

    def _reward_fn(reward, done, info):
        steering = info["steering"]
        prev_info = _Memory.info
        prev_steering = prev_info["steering"]

        steering_diff = (prev_steering - steering)
        if abs(steering_diff) > max_steering_diff:
            error = abs(steering_diff) - max_steering_diff
            jerk_penalty = steering_diff_reward_weight * (1 + error ** 2)
        else:
            jerk_penalty = 0

        # Cancel reward if the continuity constrain is violated
        if jerk_penalty > 0 and reward > 0:
            reward = 0
        # Save new info into _Memory
        _Memory.info = info
        return reward - jerk_penalty

    return _reward_fn
