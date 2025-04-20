from fastapi import APIRouter, Depends
from .actions.suggest import SuggestAction
from .schemas import PairSuggestion, SuggestResponse
from fastapi.responses import StreamingResponse


router = APIRouter(tags=["Suggest Route"])



@router.post("/suggest-pair")
async def suggest_pair(data: PairSuggestion, action: SuggestAction = Depends(SuggestAction)) -> SuggestResponse:
    return action.store_suggestion(data)