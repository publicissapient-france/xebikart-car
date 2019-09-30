
def speed(throttle_reward_weight, crash_reward_weight, crash_speed_reward_weight):
    def _reward_fn(reward, done, info):
        if done:
            # penalize the agent for getting off the road fast
            return crash_reward_weight + crash_speed_reward_weight * info["norm_throttle"]
        else:
            # step_reward + throttle_reward
            throttle_reward = throttle_reward_weight * info["ref_throttle"]
            return reward + throttle_reward
    return _reward_fn


def smooth_driving(max_steering_diff, steering_diff_reward_weight):
    def _reward_fn(reward, done, info):
        command_history = info["command_history"]
        jerk_penalty = 0
        # Take only last command into account
        for i in range(1):
            steering = command_history[-2 * (i + 1)]
            prev_steering = command_history[-2 * (i + 2)]
            steering_diff = (prev_steering - steering)

            if abs(steering_diff) > max_steering_diff:
                error = abs(steering_diff) - max_steering_diff
                jerk_penalty += steering_diff_reward_weight * (1 + error ** 2)
            else:
                jerk_penalty += 0

        # Cancel reward if the continuity constrain is violated
        if jerk_penalty > 0 and reward > 0:
            reward = 0
        return reward - jerk_penalty
    return _reward_fn
