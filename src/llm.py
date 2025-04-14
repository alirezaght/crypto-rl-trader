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

    prompt = f"""You are a trading assistant AI. Use the information provided to recommend an action on the {symbol} pair.

🧠 **Reinforcement Learning Agent Prediction:**
The RL agent suggests: **{action_descriptions[rl_action]}**

📈 **Technical Indicators:**
- RSI: {technical_indicators['rsi']}
- MACD: {technical_indicators['macd']}
- MACD Signal: {technical_indicators['macd_signal']}
- EMA 20: {technical_indicators['ema_20']}
- EMA 50: {technical_indicators['ema_50']}
- Latest Price: {technical_indicators.get('close')}

📰 **Recent News Headlines:**
"""
    for article in news_articles:
        prompt += f"- {article['title']} ({article['source']}, published {article['published']})\n"
        prompt += f"  {article.get('content', '')[:300]}...\n\n"

    prompt += """
✅ Based on the above:
- Should the user BUY, SELL, or HOLD?
- Justify your decision in 1-2 short paragraphs.
"""

    return prompt


def build_llm_prompt_for_summary(technical_indicators: Dict[str, Dict], news_articles: list, results: Dict):

    technical_prompt = ""
    for symbol, indicators in technical_indicators.items():
        technical_prompt += f"""
**{symbol} Technical Indicators:**
- RSI: {indicators['rsi']}
- MACD: {indicators['macd']}
- MACD Signal: {indicators['macd_signal']}
- EMA 20: {indicators['ema_20']}
- EMA 50: {indicators['ema_50']}
- Latest Price: {indicators.get('close')}
"""

    prompt = f"""You are a trading assistant AI. Use the information provided to recommend an action on the provided pairs.

🧠 **Reinforcement Learning Agent Prediction:**
The RL agent suggests: \n**{results}**\n

📈 **Technical Indicators for each pair:**

{technical_prompt}

📰 **Recent News Headlines:**
"""
    for article in news_articles:
        prompt += f"- {article['title']} ({article['source']}, published {article['published']})\n"
        prompt += f"  {article.get('content', '')[:300]}...\n\n"

    prompt += """
✅ Based on the above:
- What is the best action (Hold, Buy, Sell) for the user to take on each pair?
- Justify your decision in 1-2 short paragraphs.
"""

    return prompt




def query_llm(symbol: str, rl_action: int, technical_indicators: dict, news_articles: list):
    system_prompt = build_llm_prompt(symbol, rl_action, technical_indicators, news_articles)
    user_prompt = f"Give me the signal to buy, sell or hold for {symbol}."
    return query(system_prompt, user_prompt)
    
    
def query_llm_for_summary(technical_indicators: dict, news_articles: list, results: Dict):
    system_prompt = build_llm_prompt_for_summary(technical_indicators, news_articles, results)
    user_prompt = f"Give me the signal to buy, sell or hold for each symbol."
    return query(system_prompt, user_prompt)
            
            
def query(system_prompt: str, user_prompt: str):
    stream = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=True
    )

    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content