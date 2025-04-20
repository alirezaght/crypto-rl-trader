from base.action import BaseActionProtected
from base.llm import query_for_symbol
from utils.data import rank_hot_pairs


class LLMAction(BaseActionProtected):
    def query_for_one_symbol(self, symbol):
        return query_for_symbol(symbol, self.config)
    
    def query_for_hot_pairs(self):        
        yield "<thinking>Analyzing ...</thinking>"
        pairs = self.config.PAIRS        
        interval = self.config.INTERVAL        
        all_pairs = self.config.PAIRS
        top_pairs = rank_hot_pairs(all_pairs, interval=interval, days=3)[:10]
        pairs = top_pairs
        for symbol in pairs:
            yield from query_for_symbol(symbol, self.config)
    