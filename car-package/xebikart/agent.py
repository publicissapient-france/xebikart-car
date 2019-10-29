from rl_coach.agents.human_agent import HumanAgentParameters, HumanAgent
from rl_coach.core_types import ActionInfo


class XebikartHumanAgentParameters(HumanAgentParameters):
    @property
    def path(self):
        return 'xebikart.agent:XebikartHumanAgent'


class XebikartHumanAgent(HumanAgent):
    def __init__(self, *args, **kwargs):
        super(XebikartHumanAgent, self).__init__(*args, **kwargs)
        self.current_steering = 0

    def choose_action(self, curr_state):
        self.change_action_from_user()
        action = ActionInfo([self.current_steering])
        action = self.output_filter.reverse_filter(action)

        # keep constant fps
        self.clock.tick(self.max_fps)

        if not self.env.renderer.is_open:
            self.save_replay_buffer_and_exit()

        return action

    def change_action_from_user(self):
        """
        Get an action from the user keyboard
        :return: action index
        """
        env_renderer = self.env.renderer

        # the keys are the numbers on the keyboard corresponding to the action index
        if len(env_renderer.pressed_keys) > 0:
            press_key = env_renderer.pressed_keys[0]
            if press_key == 275:
                self.current_steering += 0.1
            elif press_key == 276:
                self.current_steering -= 0.1
            elif press_key == 274:
                self.current_steering = 0
