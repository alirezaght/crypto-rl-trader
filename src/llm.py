from secret_manager import get_groq_key
import requests
from groq import Groq
from typing import List, Dict, Optional

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

Output must be in this format:

**{symbol}: ACTION**
<2-3 paragraphs explanation based on technicals, RL signal, and news>

---
🧠 RL Agent Suggestion:  
{action_descriptions[rl_action]}

📊 Technical Indicators (last few 4h intervals):  
RSI: {technical_indicators['rsi']}  
MACD: {technical_indicators['macd']}  
MACD Signal: {technical_indicators['macd_signal']}  
EMA 20: {technical_indicators['ema_20']}  
EMA 50: {technical_indicators['ema_50']}  
Stochastic K: {technical_indicators['stoch_k']}  
Stochastic D: {technical_indicators['stoch_d']}  
ROC: {technical_indicators['roc']}  
ADX: {technical_indicators['adx']}  
Bollinger MA: {technical_indicators['bollinger_mavg']}  
Bollinger Upper: {technical_indicators['bollinger_hband']}  
Bollinger Lower: {technical_indicators['bollinger_lband']}  
ATR: {technical_indicators['atr']}  
OBV: {technical_indicators['obv']}

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



def build_llm_prompt_for_summary(
    technical_indicators: Dict[str, Dict], 
    news_articles: list, 
    results: Dict
) -> str:
    
    technical_prompt = ""
    for symbol, indicators in technical_indicators.items():
        technical_prompt += f"""
📊 {symbol} Indicators (4h intervals):
RSI: {indicators['rsi']}
MACD: {indicators['macd']}
MACD Signal: {indicators['macd_signal']}
EMA 20: {indicators['ema_20']}
EMA 50: {indicators['ema_50']}
Stochastic K: {indicators['stoch_k']}
Stochastic D: {indicators['stoch_d']}
ROC: {indicators['roc']}
ADX: {indicators['adx']}
Bollinger MA: {indicators['bollinger_mavg']}
Bollinger Upper: {indicators['bollinger_hband']}
Bollinger Lower: {indicators['bollinger_lband']}
ATR: {indicators['atr']}
OBV: {indicators['obv']}

"""

    news_prompt = ""
    for article in news_articles:
        news_prompt += f"- {article['title']} ({article['source']}, {article['published']})\n"
        if article.get("content"):
            news_prompt += f"  {article['content'][:300]}...\n"

    prompt = f"""
You are a confident, concise crypto trading assistant. Do not include introductions, disclaimers, or meta-comments.

For each pair below, analyze the technical indicators, reinforcement learning signal, and news headlines. Use relevant news if it provides meaningful insight.

Format exactly like this:

**SYMBOL: ACTION**
<3-5 sentence explanation using technical indicators, RL signal, and/or news. Use full sentence.>
---
Example:
**BTC/USD: BUY**
RSI and MACD both show bullish momentum. OBV is rising steadily.  
Recent ETF approval has also positively influenced sentiment.

**ETH/USD: SELL**
Bearish crossover in Stochastic Oscillator and declining RSI.  
Recent news suggests potential regulatory pressure in the short term.

---
Rules (must be followed exactly):  
- Never combine multiple results into a single paragraph  
- DO NOT include any introductions, summaries, or closing statements
- ONLY return the formatted list of results. Nothing else.
---
🧠 RL Agent Suggestions:
{results}

{technical_prompt}
📰 News Headlines:
{news_prompt}

---
""".strip()

    return prompt




def query_llm(symbol: str, rl_action: int, technical_indicators: dict, news_articles: list):
    system_prompt = build_llm_prompt(symbol, rl_action, technical_indicators, news_articles)
    user_prompt = f"Give me the signal to buy, sell or hold for {symbol}."
    yield from query(system_prompt, user_prompt)
    
    
def query_llm_for_summary(technical_indicators: dict, news_articles: list, results: Dict):
    system_prompt = build_llm_prompt_for_summary(technical_indicators, news_articles, results)
    user_prompt = f"Give me the signal to buy, sell or hold for each symbol."
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