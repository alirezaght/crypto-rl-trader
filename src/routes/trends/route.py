from fastapi import APIRouter, Depends
from .actions.trend import TrendAction
from fastapi.responses import StreamingResponse


router = APIRouter(tags=["Trend Route"])

@router.get("/llm-trend")
async def llm_trend(action: TrendAction = Depends(TrendAction)):                
    return StreamingResponse(action.get_trends())