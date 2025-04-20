from base.action import BaseActionProtected
from training.train import CryptoTrainer
import datetime
from ..schemas import PredictResponse

class PredictAction(BaseActionProtected):
    def predict(self, symbol: str):
        trainer = CryptoTrainer(symbol=symbol, interval=self.config.INTERVAL, days=self.config.WINDOW_DAYS, predict_days=self.config.PREDICT_DAYS, train=False)
        dt_from = datetime.datetime.now() - datetime.timedelta(days=self.config.WINDOW_DAYS + 14)
        dt_to = datetime.datetime.now()
        action = trainer.predict(dt_from, dt_to)
        return PredictResponse(action=action)