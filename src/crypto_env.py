import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
from utils import add_technical_indicators

class CryptoPredictionEnv(gym.Env):
    def __init__(self, df: pd.DataFrame, window_size=90, prediction_horizon=30):
        super(CryptoPredictionEnv, self).__init__()
        self.df = df.reset_index(drop=True)
        self.df = add_technical_indicators(self.df)
        self.window_size = window_size
        self.prediction_horizon = prediction_horizon
        self.current_step = 0
        self.action_space = spaces.Discrete(7)
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf,
            shape=(window_size, self.df.shape[1]), dtype=np.float32
        )

        self.action_history = []
        self.reward_history = []
        self.pct_change_history = []
        self.total_return = 0.0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = np.random.randint(
            self.window_size, len(self.df) - self.prediction_horizon - 300
        )
        self.action_history.clear()
        self.reward_history.clear()
        self.pct_change_history.clear()
        self.total_return = 0.0
        return self._get_observation(), {}

    def _get_observation(self):
        obs = self.df.iloc[self.current_step - self.window_size:self.current_step].values
        return obs.astype(np.float32)

    def step(self, action):
        window = self.df.iloc[self.current_step : self.current_step + self.prediction_horizon]
        start_price = self.df.iloc[self.current_step]["close"]
        max_price = window["close"].max()
        min_price = window["close"].min()

        max_pct_change = (max_price - start_price) / start_price * 100
        min_pct_change = (min_price - start_price) / start_price * 100
        reward = self._calculate_reward(action, max_pct_change, min_pct_change)

        reward = np.clip(reward, -1.0, 1.0)  # Normalize reward
        self.total_return += reward

        self.action_history.append(action)
        self.reward_history.append(reward)
        self.pct_change_history.append(max_pct_change)

        self.current_step += 1
        done = self.current_step >= len(self.df) - self.prediction_horizon

        return self._get_observation(), reward, done, False, {}

    def _calculate_reward(self, action, max_pct_change, min_pct_change):
        if action == 0:  # HOLD
            volatility = abs(max_pct_change - min_pct_change)
            if volatility < 1.0:
                return 0.2  # low-volatility, passive reward
            return -0.1

        if action in [1, 2, 3]:  # BUY actions
            expected_gain = max_pct_change
            size_multiplier = [0.25, 0.5, 1.0][action - 1]
            if expected_gain > 0:
                return (expected_gain / 5.0) * size_multiplier
            return -0.5 * size_multiplier

        if action in [4, 5, 6]:  # SELL actions
            expected_loss = min_pct_change
            size_multiplier = [0.25, 0.5, 1.0][action - 4]
            if expected_loss < 0:
                return (abs(expected_loss) / 5.0) * size_multiplier
            return -0.5 * size_multiplier

        return -1.0

    def render(self, mode="human"):
        print(f"Step: {self.current_step}")
        if self.reward_history:
            avg_reward = np.mean(self.reward_history)
            print(f"Average Reward: {avg_reward:.4f}")
            print(f"Last Action: {self.action_history[-1]} | Last Pct Change: {self.pct_change_history[-1]:.2f}% | Last Reward: {self.reward_history[-1]:.2f}")
