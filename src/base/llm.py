from utils.secret_manager import get_groq_key
from groq import Groq
from config_manager.config import Config
from training.train import CryptoTrainer
import datetime
from utils.news import get_all_news
from utils.data import fetch_data, add_technical_indicators, clamp_to_hour
from typing import Generator

client = Groq(api_key=get_groq_key().strip())

model = "llama3-70b-8192" # mistral-saba-24b

def build_llm_prompt(symbol: str, rl_action: int, technical_indicators: dict, news_articles: list):
    action_descriptions = {
        0: "HOLD",
        1: "BUY - slight chance of rise",
        2: "BUY - moderate chance of rise",
        3: "BUY - high chance of rise",
        4: "SELL - slight chance of drop",
        5: "SELL - moderate chance of drop",
        6: "SELL - high chance of drop",
    }

    prompt = f"""
You are a confident, concise crypto trading assistant. Do not include introductions, disclaimers, or meta-comments.

Analyze the following data and output one clear action: **BUY**, **SELL**, or **HOLD** — with a brief explanation that may reference relevant indicators or news.

Output format (must be followed exactly):

**{symbol}: ACTION**
<2-3 paragraphs explanation based on technicals, RL signal, and news>

---
🧠 RL Agent Suggestion:  
{action_descriptions[rl_action]}

📊 Technical Indicators (for current day, last week, both with interval 1d):  
RSI: {technical_indicators["1d"]['rsi']}, {technical_indicators["1w"]['rsi']}  
MACD: {technical_indicators["1d"]['macd']}, {technical_indicators["1w"]['macd']}  
MACD Signal: {technical_indicators["1d"]['macd_signal']}, {technical_indicators["1w"]['macd_signal']}  
EMA 20: {technical_indicators["1d"]['ema_20']}, {technical_indicators["1w"]['ema_20']}  
EMA 50: {technical_indicators["1d"]['ema_50']}, {technical_indicators["1w"]['ema_50']}  
Stochastic K: {technical_indicators["1d"]['stoch_k']}, {technical_indicators["1w"]['stoch_k']}  
Stochastic D: {technical_indicators["1d"]['stoch_d']}, {technical_indicators["1w"]['stoch_d']} 
ROC: {technical_indicators["1d"]['roc']}, {technical_indicators["1w"]['roc']}  
ADX: {technical_indicators["1d"]['adx']}, {technical_indicators["1w"]['adx']}  
Bollinger MA: {technical_indicators["1d"]['bollinger_mavg']}, {technical_indicators["1w"]['bollinger_mavg']}  
Bollinger Upper: {technical_indicators["1d"]['bollinger_hband']}, {technical_indicators["1w"]['bollinger_hband']}  
Bollinger Lower: {technical_indicators["1d"]['bollinger_lband']}, {technical_indicators["1w"]['bollinger_lband']}  
ATR: {technical_indicators["1d"]['atr']}, {technical_indicators["1w"]['atr']}  
OBV: {technical_indicators["1d"]['obv']}, {technical_indicators["1w"]['obv']}

📰 Relevant News (include in your decision if applicable):  
"""

    for article in news_articles:
        prompt += f"- {article['title']} ({article['source']}, {article['published']})\n"
        if article.get("content"):
            prompt += f"  {article['content'][:300]}...\n"

    prompt += f"""
---
Return only the final decision and reason, no additional commentary.
"""

    return prompt.strip()


def query_llm(symbol: str, rl_action: int, technical_indicators: dict, news_articles: list):
    system_prompt = build_llm_prompt(symbol, rl_action, technical_indicators, news_articles)
    user_prompt = f"Give me the signal to buy, sell or hold for {symbol}."
    yield from query(system_prompt, user_prompt)
    
    
def query(system_prompt: str, user_prompt: str):
    stream = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=True
    )
    yield "\n\n"
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
            
            
            
def query_for_symbol(symbol: str, config: Config) -> Generator[str, None, None]:        
        yield "<thinking>Analyzing ...</thinking>"
        trainer = CryptoTrainer(symbol=symbol, interval=config.INTERVAL, days=config.WINDOW_DAYS, predict_days=config.PREDICT_DAYS, train=False)        
        dt_from = datetime.datetime.now() - datetime.timedelta(days=config.WINDOW_DAYS + 14)
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