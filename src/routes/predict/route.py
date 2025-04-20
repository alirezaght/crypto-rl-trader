from fastapi import APIRouter, Depends
from .actions.predict import PredictAction
from .actions.llm import LLMAction
from .schemas import PredictResponse
from fastapi.responses import StreamingResponse
from typing import Literal
from base.schemas import MarketType

router = APIRouter(tags=["Predict Route"])


@router.get("/predict")
async def predict(symbol: str, action: PredictAction = Depends(PredictAction)) -> PredictResponse:    
    return action.predict(symbol)    
    
    


@router.get("/llm-stream")
async def llm_stream(symbol: str, action: LLMAction = Depends(LLMAction)):                
    return StreamingResponse(action.query_for_one_symbol(symbol))


@router.get("/llm-summary")
async def llm_summary(type: MarketType = "crypto", action: LLMAction = Depends(LLMAction)):        
    return StreamingResponse(action.query_for_hot_pairs(type))



