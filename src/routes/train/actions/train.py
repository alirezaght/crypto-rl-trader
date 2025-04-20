from base.action import BaseActionProtected
from fastapi import HTTPException
from training.basket import Basket
import datetime
from ..schemas import TrainResponse

class TrainAction(BaseActionProtected):
    def train(self) -> TrainResponse:        
        if self.user.get("role") != "trainer":
            raise HTTPException(status_code=403, detail="Access denied: trainer role required")
        
        pairs = self.config.PAIRS
        predict_days = self.config.PREDICT_DAYS
        interval = self.config.INTERVAL
        window_days = self.config.WINDOW_DAYS
        
        basket = Basket(pairs, interval=interval, days=window_days, predict_days=predict_days)
        results = basket.get_signals(datetime.datetime.now())
        return TrainResponse(results=results)
    