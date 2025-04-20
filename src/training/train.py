from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
import numpy as np
from .crypto_env import CryptoPredictionEnv
import matplotlib.pyplot as plt
from utils.data import get_candle_count, fetch_data, clamp_to_hour
import datetime
from utils.storage import download_from_gcs, gcs_file_exists, upload_to_gcs
import os
from config_manager.schemas import Config

class CryptoTrainer:
    def __init__(self, symbol: str, crypto_config: Config, stock_config: Config, train=True):
        self.symbol = symbol        
        self.interval = crypto_config.interval if "/" in symbol else stock_config.interval
        self.days = crypto_config.window_days if "/" in symbol else stock_config.window_days
        self.window_size = get_candle_count(self.days, self.interval, "crypto" if "/" in symbol else "stock")
        self.predict_days = crypto_config.predict_days if "/" in symbol else stock_config.predict_days
        self.predict_horizon = get_candle_count(self.predict_days, self.interval, "crypto" if "/" in symbol else "stock")
        self.file_name = f"{symbol}_{self.days}_{self.predict_days}_{self.interval}".replace("/", "_")
        self.train = train  
        self.model_path = f"/tmp/{self.file_name}.zip"
        self.vec_path = f"/tmp/vec_{self.file_name}.pkl"      
        model_exists = gcs_file_exists(f"models/{self.file_name}.zip") and gcs_file_exists(f"models/vec_{self.file_name}.pkl")
        self.train = train
        self.loopback_days = 500

        if not model_exists:
            if not train:
                raise FileNotFoundError(f"Model files for {self.file_name} not found.")
            print(f"Training model for {self.symbol}")
            df = fetch_data(symbol=symbol, interval=self.interval, lookback_days=self.loopback_days)
            df = df.drop(columns=["timestamp"])
            env = CryptoPredictionEnv(df=df, window_size=self.window_size, prediction_horizon=self.predict_horizon)
            vec_env = DummyVecEnv([lambda: env])
            vec_env = VecNormalize(vec_env, norm_obs=True, norm_reward=True, clip_reward=1.0)
            model = PPO("MlpPolicy", vec_env, verbose=1)
            model.learn(total_timesteps=200_000)
            model.save(self.model_path)
            vec_env.save(self.vec_path)
            
            upload_to_gcs(self.model_path, f"models/{self.file_name}.zip")
            upload_to_gcs(self.vec_path, f"models/vec_{self.file_name}.pkl")
        elif not os.path.exists(self.model_path) or not os.path.exists(self.vec_path):
            print(f"Model exists for {self.symbol}. Downloading...")
            download_from_gcs(f"models/{self.file_name}.zip", self.model_path)
            download_from_gcs(f"models/vec_{self.file_name}.pkl", self.vec_path)
            
        
    def predict(self, from_date: datetime.datetime, to_date: datetime.datetime) -> int:
        df = fetch_data(symbol=self.symbol, interval=self.interval, start_date=clamp_to_hour(from_date), end_date=clamp_to_hour(to_date))
        if len(df) < self.window_size:
            raise ValueError("Not enough data to make a prediction.")
        df_no_ts = df.drop(columns=["timestamp"])
        env = CryptoPredictionEnv(df=df_no_ts, window_size=self.window_size, prediction_horizon=self.predict_horizon)
        env.current_step = self.window_size
        vec_env = DummyVecEnv([lambda: env])
        vec_env = VecNormalize.load(self.vec_path, vec_env)
        vec_env.training = False
        vec_env.norm_reward = False
        model = PPO.load(self.model_path, env=vec_env)

        obs = vec_env.normalize_obs(env._get_observation())  

        action, _ = model.predict(obs, deterministic=True)
        action = int(action)
        return action
        
    def fetch_price_at(self, dt: datetime.datetime) -> dict:
        df = fetch_data(symbol=self.symbol, interval=self.interval,
                        start_date=clamp_to_hour(dt - datetime.timedelta(days=1)),
                        end_date=clamp_to_hour(dt + datetime.timedelta(days=1)))
        df = df.set_index("timestamp")
        nearest = df.iloc[df.index.get_indexer([dt], method="nearest")]
        return nearest.iloc[0].to_dict()

    