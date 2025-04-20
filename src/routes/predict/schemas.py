from pydantic import BaseModel

class PredictResponse(BaseModel):
    action: int
