from base.action import BaseActionProtected
from training.train import CryptoTrainer
import datetime
from ..schemas import PredictResponse
from config_manager.config import get_config

class PredictAction(BaseActionProtected):
    def predict(self, symbol: str):
        config = get_config("crypto") if "/" in symbol else get_config("stock")
        trainer = CryptoTrainer(symbol=symbol, interval=config.interval, days=config.window_days, predict_days=config.predict_days, train=False)        
        action, confidence = trainer.predict(datetime.datetime.now())
        return PredictResponse(action=action)