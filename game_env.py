import gym
from gym import spaces
import numpy as np
from game import Game


class RobotTourEnv(gym.Env):
    def __init__(self) -> None:
        super(RobotTourEnv, self).__init__()
        self.game = Game()
        self.action_space = spaces.Discrete(7)
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(4,), dtype=np.float32
        )

        return None

    def step(self, action: int) -> (np.ndarray, float, bool):
        reward = 0
        done = False
        state = {}
        previous_score = self.game.judge.get_score()

        if action == 6:
            reward = previous_score - self.game.end_run()
            state = self.game.get_state()
            return state, reward, True

        elif action == 0:
            self.game.move_forward()
        elif action == 1:
            self.game.move_backward()
        elif action == 2:
            self.game.robot.increase_speed()
        elif action == 3:
            self.game.robot.decrease_speed()
        elif action == 4:
            self.game.robot.increase_angle()
        elif action == 5:
            self.game.robot.decrease_angle()

        self.game.render()

        state = self.game.get_state()
        reward = previous_score - self.game.judge.get_score()
        done = self.game.is_over()

        return state, reward, done

    def reset(self) -> np.ndarray:
        self.game = Game()
        self.game.render()

        return self.game.get_state()

    def render(self) -> None:
        self.game.run("rl")

        return None
