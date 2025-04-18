from pydantic import BaseModel
from typing import Dict

class TrainResponse(BaseModel):
    results: Dict[int, str]