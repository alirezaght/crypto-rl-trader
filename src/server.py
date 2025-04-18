from fastapi import FastAPI
import datetime
from train import CryptoTrainer
from dotenv import load_dotenv
from main import config
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from security import get_current_user
from fastapi import HTTPException
from llm import query_llm, query_llm_for_summary
from fastapi.responses import StreamingResponse
from news import get_all_news
from utils import add_technical_indicators, fetch_data
from pydantic import BaseModel
from firestore import store_suggestion
from fastapi import Request
from basket import Basket
from utils import rank_hot_pairs, clamp_to_hour, chunk_dict

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
    window_days = config.get("WINDOW_DAYS", 90)
    return {
        "pairs": pairs,
        "predict_days": predict_days,
        "interval": interval,
        "window_days": window_days
    }
    
@app.get("/train")
async def train(user=Depends(get_current_user)):    
    if user.get("role") != "trainer":
        raise HTTPException(status_code=403, detail="Access denied: trainer role required")
    
    pairs = config.get("PAIRS")
    predict_days = config.get("PREDICT_DAYS", 30)
    interval = config.get("INTERVAL", "4h")
    window_days = config.get("WINDOW_DAYS", 90)
    
    basket = Basket(pairs, interval=interval, days=window_days, predict_days=predict_days)
    results = basket.get_signals(datetime.datetime.now())
    return {"results": results}


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
        technical_snapshot = {}
        df = fetch_data(symbol=symbol, interval="1d", start_date=clamp_to_hour(dt_from), end_date=clamp_to_hour(dt_to))
        df_with_indicators = add_technical_indicators(df)
        latest_row = df_with_indicators.iloc[-1:].round(2)        
        technical_snapshot["1d"] = latest_row
        
        df = fetch_data(symbol=symbol, interval="1d", start_date=clamp_to_hour(dt_from), end_date=clamp_to_hour(dt_to - datetime.timedelta(days=7)))
        df_with_indicators = add_technical_indicators(df)
        latest_row = df_with_indicators.iloc[-1:].round(2)
        technical_snapshot["1w"] = latest_row
        
        
        
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

@app.get("/llm-summary")
async def llm_summary(user=Depends(get_current_user)):
    def event_generator():
        yield "<thinking>Analyzing ...</thinking>"
        pairs = config.get("PAIRS")
        predict_days = config.get("PREDICT_DAYS", 30)
        interval = config.get("INTERVAL", "4h")
        window_days = config.get("WINDOW_DAYS", 90)        
        all_pairs = config.get("PAIRS")
        top_pairs = rank_hot_pairs(all_pairs, interval=interval, days=3)[:10]
        pairs = top_pairs
        yield "<thinking>Predicting ...</thinking>"
        basket = Basket(pairs, interval=interval, days=window_days, predict_days=predict_days, train=False)
        results = basket.get_signals(datetime.datetime.now())                
        yield "<thinking>Fetching recent articles ...</thinking>"
        news_articles = get_all_news()
        yield "<thinking>Adding technical indicators ...</thinking>"
        dt_from = datetime.datetime.now() - datetime.timedelta(days=window_days + 14)
        dt_to = datetime.datetime.now()        
        technical_snapshots = {}
        for symbol in pairs:
            technical_snapshots[symbol] = {}
            df = fetch_data(symbol=symbol, interval="1d", start_date=clamp_to_hour(dt_from), end_date=clamp_to_hour(dt_to))
            df_with_indicators = add_technical_indicators(df)
            latest_row = df_with_indicators.iloc[-1:].round(2)            
            technical_snapshots[symbol]["1d"] = latest_row
            
            df = fetch_data(symbol=symbol, interval="1d", start_date=clamp_to_hour(dt_from), end_date=clamp_to_hour(dt_to - datetime.timedelta(days=7)))
            df_with_indicators = add_technical_indicators(df)
            latest_row = df_with_indicators.iloc[-1:].round(2)
            technical_snapshots[symbol]["1w"] = latest_row
            
            
        yield "<thinking>Summarizing ...</thinking>"
        for i, chunk in enumerate(chunk_dict(technical_snapshots, chunk_size=3)):
            chunk_pairs = list(chunk.keys())
            chunk_results = {k: results.get(k) for k in chunk_pairs}
            yield f"<thinking>Summarizing ...</thinking>"
            yield from query_llm_for_summary(chunk, news_articles, chunk_results)                             
            yield "\n\n"
    

    return StreamingResponse(event_generator(), media_type="text/event-stream")