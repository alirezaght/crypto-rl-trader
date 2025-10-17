from llm.predict_llm import PredictLLM
from base.action import BaseActionProtected
from utils.data import rank_hot_pairs
from typing import Literal
from config_manager.config import get_config
from config_manager.schemas import Config
from base.schemas import MarketType
import random

class LLMAction(BaseActionProtected):
    
    
    def __init__(self):
        super().__init__()
        self.crypto_llm = PredictLLM(model="llama-3.3-70b-versatile", langfuse_prompt="crypto")
        self.stock_llm = PredictLLM(model="llama-3.3-70b-versatile", langfuse_prompt="stock")
        
    
    def query_for_one_symbol(self, symbol):
        if "/" in symbol:
            return self.crypto_llm.query_for_symbol(symbol)
        else:
            return self.stock_llm.query_for_symbol(symbol)
    
    def query_for_hot_pairs(self, type: MarketType):        
        yield "<thinking>Analyzing ...</thinking>"
        
        
        config: Config = get_config(type)
        
        llm: PredictLLM = None
        
        if type == "crypto":            
            llm = self.crypto_llm
        elif type == "stock":            
            llm = self.stock_llm
            
        if llm:
            symbols = rank_hot_pairs(config.symbols, interval=config.interval, days=7)[:10]
            if len(symbols) == 0:
                symbols = random.sample(config.symbols, k=min(10, len(config.symbols)))
            for symbol in symbols:
                yield from llm.query_for_symbol(symbol)
    