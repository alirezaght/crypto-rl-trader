import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
from utils.data import add_technical_indicators

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
            if volatility < 0.2:
                return 1  
            return -1
        
        
        if action == 1:
            if max_pct_change >= 0.25 and max_pct_change < 0.5:
                return 1
            elif max_pct_change > 0.20:
                return abs(max_pct_change - 0.20)            
            else:
                return -1
            
        if action == 2:
            if max_pct_change >= 0.5 and max_pct_change < 0.75:
                return 1
            elif max_pct_change > 0.45:
                return abs(max_pct_change - 0.45)            
            else:
                return -1
            
        if action == 3:
            if max_pct_change >= 0.75 and max_pct_change <= 1:
                return 1
            elif max_pct_change > 0.70:
                return abs(max_pct_change - 0.70)            
            else:
                return -1

        if action == 4:
            change = abs(min_pct_change)
            if change >= 0.25 and change < 0.5:
                return 1
            elif change > 0.20:
                return abs(change - 0.20)            
            else:
                return -1
            
        if action == 5:
            change = abs(min_pct_change)
            if change >= 0.50 and change < 0.75:
                return 1
            elif change > 0.45:
                return abs(change - 0.45)            
            else:
                return -1
            
        if action == 6:
            change = abs(min_pct_change)
            if change >= 0.75 and change <= 1:
                return 1
            elif change > 0.70:
                return abs(change - 0.70)            
            else:
                return -1        

        return -1.0

    def render(self, mode="human"):
        print(f"Step: {self.current_step}")
        if self.reward_history:
            avg_reward = np.mean(self.reward_history)
            print(f"Average Reward: {avg_reward:.4f}")
            print(f"Last Action: {self.action_history[-1]} | Last Pct Change: {self.pct_change_history[-1]:.2f}% | Last Reward: {self.reward_history[-1]:.2f}")
