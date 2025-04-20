from pydantic import BaseModel
from typing import List

class ConfigResponse(BaseModel):
    pairs: List[str]
    predict_days: int
    interval: str
    window_days: int