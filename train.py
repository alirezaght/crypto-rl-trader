from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
import numpy as np
from crypto_env import CryptoPredictionEnv
import os
import matplotlib.pyplot as plt
from utils import get_candle_count, fetch_data
import datetime


class CryptoTrainer:
    def __init__(self, symbol="BTCUSDT", interval="4h", days=90, predict_days = 30):
        self.symbol = symbol
        self.interval = interval
        self.days = days
        self.window_size = get_candle_count(days, interval)
        self.predict_horizon = get_candle_count(predict_days, interval)
        self.file_name = f"{symbol}_{days}_{predict_days}_{interval}"        
        if not (os.path.exists(f"vec_{self.file_name}.pkl") and os.path.exists(f"{self.file_name}.zip")):
            print(f"Training model for {self.symbol}")
            df = fetch_data(symbol=symbol, interval=interval, lookback_days=500)
            df = df.drop(columns=["timestamp"])
            env = CryptoPredictionEnv(df=df, window_size=self.window_size, prediction_horizon=self.predict_horizon)
            vec_env = DummyVecEnv([lambda: env])
            vec_env = VecNormalize(vec_env, norm_obs=True, norm_reward=True, clip_reward=1.0)
            model = PPO("MlpPolicy", vec_env, verbose=1)
            model.learn(total_timesteps=200_000)
            model.save(self.file_name)
            vec_env.save(f"vec_{self.file_name}.pkl")
        else:
            print(f"Model exists for {self.symbol}.")
        
    def predict(self, from_date: datetime.datetime, to_date: datetime.datetime) -> int:
        df = fetch_data(symbol=self.symbol, interval=self.interval, start_date=from_date, end_date=to_date)
        if len(df) < self.window_size:
            raise ValueError("Not enough data to make a prediction.")
        df_no_ts = df.drop(columns=["timestamp"])
        env = CryptoPredictionEnv(df=df_no_ts, window_size=self.window_size, prediction_horizon=self.predict_horizon)
        env.current_step = self.window_size
        vec_env = DummyVecEnv([lambda: env])
        vec_env = VecNormalize.load(f"vec_{self.file_name}.pkl", vec_env)
        vec_env.training = False
        vec_env.norm_reward = False
        model = PPO.load(self.file_name, env=vec_env)

        obs = vec_env.normalize_obs(env._get_observation())  

        action, _ = model.predict(obs, deterministic=True)
        action = int(action)
        return action
        
    def fetch_price_at(self, dt: datetime.datetime) -> dict:
        df = fetch_data(symbol=self.symbol, interval=self.interval,
                        start_date=dt - datetime.timedelta(days=1),
                        end_date=dt + datetime.timedelta(days=1))
        df = df.set_index("timestamp")
        nearest = df.iloc[df.index.get_indexer([dt], method="nearest")]
        return nearest.iloc[0].to_dict()

    