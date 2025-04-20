from base.action import BaseActionProtected
from training.train import CryptoTrainer
import datetime
from ..schemas import PredictResponse
from config_manager.config import get_config

class PredictAction(BaseActionProtected):
    def predict(self, symbol: str):
        config = get_config("crypto") if "/" in symbol else get_config("stock")
        trainer = CryptoTrainer(symbol=symbol, interval=config.interval, days=config.window_days, predict_days=config.predict_days, train=False)
        dt_from = datetime.datetime.now() - datetime.timedelta(days=config.window_days + 14)
        dt_to = datetime.datetime.now()
        action, confidence = trainer.predict(dt_from, dt_to)
        return PredictResponse(action=action)