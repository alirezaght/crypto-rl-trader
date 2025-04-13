from fastapi import FastAPI
import datetime
from train import CryptoTrainer
from dotenv import load_dotenv
from main import config
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from security import get_current_user
from fastapi import HTTPException
from llm import query_llm
from fastapi.responses import StreamingResponse
from news import get_all_news
from utils import add_technical_indicators, fetch_data
from pydantic import BaseModel
from firestore import store_suggestion
from fastapi import Request

load_dotenv()

app = FastAPI(    
    docs_url=None,    
    redoc_url=None,    
    openapi_url=None 
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/predict")
async def predict(symbol: str, user=Depends(get_current_user)):    
    trainer = CryptoTrainer(symbol=symbol, interval=config.get("INTERVAL", "4h"), days=config.get("WINDOW_DAYS", 90), predict_days=config.get("PREDICT_DAYS", 30), train=False)
    dt_from = datetime.datetime.now() - datetime.timedelta(days=config.get("WINDOW_DAYS", 90) + 14)
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
async def train(symbol: str, user=Depends(get_current_user)):    
    if user.get("role") != "trainer":
        raise HTTPException(status_code=403, detail="Access denied: trainer role required")
    trainer = CryptoTrainer(symbol=symbol, interval=config.get("INTERVAL", "4h"), days=config.get("WINDOW_DAYS", 90), predict_days=config.get("PREDICT_DAYS", 30), train=True)
    dt_from = datetime.datetime.now() - datetime.timedelta(days=config.get("WINDOW_DAYS", 90) + 14)
    dt_to = datetime.datetime.now()
    action = trainer.predict(dt_from, dt_to)
    return {"action": action}


@app.get("/llm-stream")
async def llm_stream(symbol: str, user=Depends(get_current_user)):        
    def event_generator():
        yield "<thinking>Analyzing ...</thinking>"
        trainer = CryptoTrainer(symbol=symbol, interval=config.get("INTERVAL", "4h"), days=config.get("WINDOW_DAYS", 90), predict_days=config.get("PREDICT_DAYS", 30), train=False)        
        dt_from = datetime.datetime.now() - datetime.timedelta(days=config.get("WINDOW_DAYS", 90) + 14)
        dt_to = datetime.datetime.now()
        yield "<thinking>Fetching historical data ...</thinking>"
        action = trainer.predict(dt_from, dt_to)
        yield "<thinking>Fetching recent articles ...</thinking>"
        news_articles = get_all_news()
        yield "<thinking>Adding technical indicators ...</thinking>"
        df = fetch_data(symbol=symbol, interval="4h", start_date=dt_from, end_date=dt_to)
        df_with_indicators = add_technical_indicators(df)
        latest_row = df_with_indicators.iloc[-1]
        technical_snapshot = latest_row.drop(labels=["timestamp"]).to_dict()
        
        
        for chunk in query_llm(symbol, action, technical_snapshot, news_articles):
            yield chunk
    

    return StreamingResponse(event_generator(), media_type="text/event-stream")

class PairSuggestion(BaseModel):
    pair: str

def get_client_ip(request: Request) -> str:
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host

@app.post("/suggest-pair")
async def suggest_pair(data: PairSuggestion, request: Request, user=Depends(get_current_user)):
    store_suggestion(data.pair, get_client_ip(request))
    return {"status": "ok"}