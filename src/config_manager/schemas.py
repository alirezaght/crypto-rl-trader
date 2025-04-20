from pydantic import BaseModel
from typing import List

class Config(BaseModel):
    interval: str
    symbols: List[str]
    predict_days: int
    window_days: int
    
class DBConfig(BaseModel):
    INTERVAL: str
    INTERVAL_STOCK: str
    PAIRS: List[str]
    STOCKS: List[str]
    PREDICT_DAYS: int
    PREDICT_DAYS_STOCK: int
    WINDOW_DAYS: int
    WINDOW_DAYS_STOCK: int
    
