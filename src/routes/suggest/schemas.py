from pydantic import BaseModel

class PairSuggestion(BaseModel):
    pair: str
    
class SuggestResponse(BaseModel):
    status: str