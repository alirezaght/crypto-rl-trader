from utils.secret_manager import get_groq_key
from groq import Groq
from groq.types.chat.chat_completion_chunk import ChatCompletionChunk
from training.train import CryptoTrainer, PredictionResult
import datetime
from utils.news import get_all_crypto_news, get_all_stock_news
from utils.data import fetch_data, add_technical_indicators, clamp_to_hour
from typing import Generator
from utils.langfuse import get_langfuse
from .action import BaseActionProtected
from config_manager.config import get_config


class BaseLLM(BaseActionProtected):
    def __init__(self, model: str = "llama3-70b-8192", langfuse_prompt: str = "crypto"):
        super().__init__()        
        self.client = Groq(api_key=get_groq_key().strip())
        self.model = model
        self.langfuse_prompt = langfuse_prompt
        self.prompt_template = get_langfuse().get_prompt(langfuse_prompt)

    def build_llm_prompt(self, symbol: str, rl_action: PredictionResult, technical_indicators: dict, news_articles: list):
        action_descriptions = {
            0: "HOLD",
            1: "BUY - slight chance of rise",
            2: "BUY - moderate chance of rise",
            3: "BUY - high chance of rise",
            4: "SELL - slight chance of drop",
            5: "SELL - moderate chance of drop",
            6: "SELL - high chance of drop",
        }
        latest_row_1d = technical_indicators["1d"].iloc[-1] if technical_indicators["1d"] is not None else None
        latest_row_1w = technical_indicators["1w"].iloc[-1] if technical_indicators["1w"] is not None else None
        
        if technical_indicators["1d"] is not None and len(technical_indicators["1d"]) >= 2:
            start_price = technical_indicators["1d"]["close"].iloc[0]
            end_price = technical_indicators["1d"]["close"].iloc[-1]
            days = (technical_indicators["1d"]["timestamp"].iloc[-1] - technical_indicators["1d"]["timestamp"].iloc[0]).days
            price_change = ((end_price - start_price) / start_price) * 100
            price_summary = (
                f"{symbol} has moved from ${start_price:.2f} to ${end_price:.2f} "
                f"over the last {days} days, a change of {price_change:.2f}%."
            )
        else:
            price_summary = "Price summary unavailable due to insufficient data."
        
        technical = f"""
    RSI: {latest_row_1d['rsi'].round(3) if latest_row_1d is not None else "No Data"}, {latest_row_1w['rsi'].round(3) if latest_row_1w is not None else "No Data"}  
    MACD: {latest_row_1d['macd'].round(3) if latest_row_1d is not None else "No Data"}, {latest_row_1w['macd'].round(3) if latest_row_1w is not None else "No Data"}  
    MACD Signal: {latest_row_1d['macd_signal'].round(3) if latest_row_1d is not None else "No Data"}, {latest_row_1w['macd_signal'].round(3) if latest_row_1w is not None else "No Data"}  
    EMA 20: {latest_row_1d['ema_20'].round(3) if latest_row_1d is not None else "No Data"}, {latest_row_1w['ema_20'].round(3) if latest_row_1w is not None else "No Data"}  
    EMA 50: {latest_row_1d['ema_50'].round(3) if latest_row_1d is not None else "No Data"}, {latest_row_1w['ema_50'].round(3) if latest_row_1w is not None else "No Data"}  
    Stochastic K: {latest_row_1d['stoch_k'].round(3) if latest_row_1d is not None else "No Data"}, {latest_row_1w['stoch_k'].round(3) if latest_row_1w is not None else "No Data"}  
    Stochastic D: {latest_row_1d['stoch_d'].round(3) if latest_row_1d is not None else "No Data"}, {latest_row_1w['stoch_d'].round(3) if latest_row_1w is not None else "No Data"}  
    ROC: {latest_row_1d['roc'].round(3) if latest_row_1d is not None else "No Data"}, {latest_row_1w['roc'].round(3) if latest_row_1w is not None else "No Data"}  
    ADX: {latest_row_1d['adx'].round(3) if latest_row_1d is not None else "No Data"}, {latest_row_1w['adx'].round(3) if latest_row_1w is not None else "No Data"}  
    Bollinger MA: {latest_row_1d['bollinger_mavg'].round(3) if latest_row_1d is not None else "No Data"}, {latest_row_1w['bollinger_mavg'].round(3) if latest_row_1w is not None else "No Data"}  
    Bollinger Upper: {latest_row_1d['bollinger_hband'].round(3) if latest_row_1d is not None else "No Data"}, {latest_row_1w['bollinger_hband'].round(3) if latest_row_1w is not None else "No Data"}  
    Bollinger Lower: {latest_row_1d['bollinger_lband'].round(3) if latest_row_1d is not None else "No Data"}, {latest_row_1w['bollinger_lband'].round(3) if latest_row_1w is not None else "No Data"}  
    ATR: {latest_row_1d['atr'].round(3) if latest_row_1d is not None else "No Data"}, {latest_row_1w['atr'].round(3) if latest_row_1w is not None else "No Data"}  
    OBV: {latest_row_1d['obv'].round(3) if latest_row_1d is not None else "No Data"}, {latest_row_1w['obv'].round(3) if latest_row_1w is not None else "No Data"}
        """
        news = ""
        for article in news_articles:
            news += f"- {article['title']} ({article['source']}, {article['published']})\n"
            if article.get("content"):
                news += f"  {article['content'][:300]}...\n"
        
        

        prompt = self.prompt_template.compile(
            SYMBOL=symbol,
            RLRESULT=action_descriptions[rl_action.action],
            CONFIDENCE=rl_action.confidence,
            TECHNICAL=technical,
            NEWS=news,
            PRICESUMMARY=price_summary,
        )
        
        return prompt.strip()


    def query_llm(self, symbol: str, rl_action: PredictionResult, technical_indicators: dict, news_articles: list):
        system_prompt = self.build_llm_prompt(symbol, rl_action, technical_indicators, news_articles)
        user_prompt = f"Give me the signal to buy, sell or hold for {symbol}."
        yield from self. query(system_prompt, user_prompt)
    
    
    def query(self, system_prompt: str, user_prompt: str):
        trace = get_langfuse().trace(name=f"{self.langfuse_prompt}-trace")
        messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        
        generation = trace.generation(
            name=f"{self.langfuse_prompt}-generation",
            model=self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
        )
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True
        )
        full_response = ""
        usage = None
        yield "\n\n"
        for chunk in stream:
            chunk: ChatCompletionChunk
            if chunk.choices and chunk.choices[0].delta.content:            
                if chunk.usage:
                    usage = chunk.usage
                content_chunk = chunk.choices[0].delta.content
                full_response += content_chunk            
                yield content_chunk
                
        generation.end(
            output=full_response,
            usage=usage,   
        )

        trace.update()
            
            
            
    def query_for_symbol(self, symbol: str) -> Generator[str, None, None]:              
        crypto = True if "/" in symbol else False
        config = get_config("crypto" if crypto else "stock")
        dt_from = datetime.datetime.now() - datetime.timedelta(days=config.window_days)
        dt_to = datetime.datetime.now()
        yield "<thinking>Analyzing ...</thinking>"
        try:                        
            trainer = CryptoTrainer(symbol=symbol, crypto_config=get_config("crypto"), stock_config=get_config("stock"), train=False)                    
            yield "<thinking>Fetching historical data ...</thinking>"
            rl_result = trainer.predict(dt_to)
        except Exception as e:
            yield f"<thinking>Couldn't process {symbol}...</thinking>"
            rl_result = PredictionResult(action=0, confidence=-1)
            
        yield "<thinking>Fetching recent articles ...</thinking>"
        news_articles = get_all_crypto_news() if "/" in symbol else get_all_stock_news()
        yield "<thinking>Adding technical indicators ...</thinking>"
        technical_snapshot = {}
        try:
            df = fetch_data(symbol=symbol, interval="1d", start_date=clamp_to_hour(dt_from), end_date=clamp_to_hour(dt_to))
            df_with_indicators = add_technical_indicators(df)            
            technical_snapshot["1d"] = df_with_indicators
        except Exception as e:
            technical_snapshot["1d"] = None
        
        try:
            df = fetch_data(symbol=symbol, interval="1w" if crypto else "1wk", start_date=clamp_to_hour(dt_from), end_date=clamp_to_hour(dt_to))
            df_with_indicators = add_technical_indicators(df)            
            technical_snapshot["1w"] = df_with_indicators
        except Exception as e:
            technical_snapshot["1w"] = None
        
        
        
        for chunk in self.query_llm(symbol, rl_result, technical_snapshot, news_articles):
            yield chunk
        
            