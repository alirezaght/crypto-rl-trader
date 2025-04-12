from fastapi import FastAPI
import datetime
from train import CryptoTrainer
from dotenv import load_dotenv
from main import config
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from security import get_current_user
from fastapi import HTTPException

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/predict")
async def predict(symbol: str, days: int = 90, predict_days: int = 30, user=Depends(get_current_user)):    
    trainer = CryptoTrainer(symbol=symbol, days=days, predict_days=predict_days, train=False)
    dt_from = datetime.datetime.now() - datetime.timedelta(days=days + 14)
    dt_to = datetime.datetime.now()
    action = trainer.predict(dt_from, dt_to)
    return {"action": action}


@app.get("/config")
async def available_pairs(user=Depends(get_current_user)):
    pairs = config.get("PAIRS")
    predict_days = config.get("PREDICT_DAYS", 30)
    interval = config.get("INTERVAL", "4h")
    windoew_days = config.get("WINDOW_DAYS", 90)
    return {
        "pairs": pairs,
        "predict_days": predict_days,
        "interval": interval,
        "window_days": windoew_days
    }
    
@app.get("/train")
async def train(symbol: str, days: int = 90, predict_days: int = 30, user=Depends(get_current_user)):    
    if user.get("role") != "trainer":
        raise HTTPException(status_code=403, detail="Access denied: trainer role required")
    trainer = CryptoTrainer(symbol=symbol, days=days, predict_days=predict_days, train=True)
    dt_from = datetime.datetime.now() - datetime.timedelta(days=days + 14)
    dt_to = datetime.datetime.now()
    action = trainer.predict(dt_from, dt_to)
    return {"action": action}