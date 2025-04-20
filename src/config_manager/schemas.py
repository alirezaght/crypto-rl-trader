from pydantic import BaseModel
from typing import List

class Config(BaseModel):
    INTERVAL: str
    PAIRS: List[str]
    PREDICT_DAYS: int
    WINDOW_DAYS: int