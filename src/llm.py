from secret_manager import get_groq_key
import requests
from groq import Groq

client = Groq(api_key=get_groq_key().strip())

model = "llama3-70b-8192" # mistral-saba-24b

def build_llm_prompt(symbol: str, rl_action: int, technical_indicators: dict, news_articles: list):
    action_descriptions = {
        0: "HOLD",
        1: "BUY - slight chance of 25% rise",
        2: "BUY - moderate chance of 50% rise",
        3: "BUY - high chance of >50% rise",
        4: "SELL - slight chance of <25% drop",
        5: "SELL - moderate chance of 50% drop",
        6: "SELL - high chance of >50% drop",
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




def query_llm(symbol: str, rl_action: int, technical_indicators: dict, news_articles: list):
    system_prompt = build_llm_prompt(symbol, rl_action, technical_indicators, news_articles)
    user_prompt = f"Give me the signal to buy, sell or hold for {symbol}."
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
    
    
    