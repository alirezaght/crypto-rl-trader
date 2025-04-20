from pydantic import BaseModel
from typing import List

class ConfigResponse(BaseModel):
    symbols: List[str]
    predict_days: int
    predict_days_stock: int
    interval: str
    interval_stock: str
    window_days: int
    window_days_stock: int