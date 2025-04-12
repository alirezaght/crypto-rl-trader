from fastapi import FastAPI
import datetime
from train import CryptoTrainer
from dotenv import load_dotenv
from main import config
load_dotenv()

app = FastAPI()


@app.get("/predict")
async def predict(symbol: str, days: int = 90, predict_days: int = 30):    
    trainer = CryptoTrainer(symbol=symbol, days=days, predict_days=predict_days, train=False)
    dt_from = datetime.datetime.now() - datetime.timedelta(days=days + 14)
    dt_to = datetime.datetime.now()
    action = trainer.predict(dt_from, dt_to)
    return {"action": action}


@app.get("/config")
async def available_pairs():
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
    
