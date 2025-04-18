from fastapi import APIRouter, Depends
from .actions.get_config import GetConfigAction
from .schemas import ConfigResponse

router = APIRouter(tags=["Config Route"])

@router.get("/config")
async def available_pairs(action: GetConfigAction = Depends(GetConfigAction)) -> ConfigResponse:
    return action.get()
    