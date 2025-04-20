from base.action import BaseActionProtected
from fastapi import HTTPException
from training.basket import Basket
import datetime
from ..schemas import TrainResponse
from config_manager.config import get_config

class TrainAction(BaseActionProtected):
    def train(self) -> TrainResponse:        
        if self.user.get("role") != "trainer":
            raise HTTPException(status_code=403, detail="Access denied: trainer role required")
        
        symbols = self.db_config.PAIRS + self.db_config.STOCKS        
        
        basket = Basket(symbols, get_config("crypto"), get_config("stock"), train=True)
        results = basket.get_signals(datetime.datetime.now())
        return TrainResponse(results=results)
    