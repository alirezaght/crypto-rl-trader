from fastapi import APIRouter, Depends
from .actions.train import TrainAction
from .schemas import TrainResponse
router = APIRouter(tags=["Train Route"])



@router.get("/train")
async def train(action=Depends(TrainAction)) -> TrainResponse:    
    return action.train()
    