from base.action import BaseActionProtected
from llm.trend_llm import TrendLLM
import praw
from utils.secret_manager import get_secret
from datetime import datetime
from utils.redis_cache import redis_cache
import random

_reddit = None
def get_reddit():
    global _reddit
    if _reddit is None:
        _reddit = praw.Reddit(
            user_agent="Trend Analysis Bot",
            client_id=get_secret('reddit-client-id'),
            client_secret=get_secret('reddit-secret'), 
            username=get_secret('reddit-username'),
            password=get_secret('reddit-password')           
            )
    return _reddit
   

@redis_cache(ttl=3600 * 4)
def fetch_trends(subreddit: str, limit=10):
    data = []
    for submission in get_reddit().subreddit(subreddit).hot(limit=10):
        data.append({
            "subreddit": subreddit,
            "title": submission.title,
            "content": submission.selftext[:500],
            "score": submission.score,
            "comments": submission.num_comments,
            "url": submission.url,
            "published": datetime.utcfromtimestamp(submission.created_utc).isoformat()
        })
    return random.sample(data, k=limit)

class TrendAction(BaseActionProtected):
    def __init__(self):
        super().__init__()
        self.llm = TrendLLM()        
        
        self.subreddits = [
    "CryptoCurrency", "CryptoMarkets", "cryptomoonshots", "Altcoin", "CryptoTechnology",
    "Stocks", "WallStreetBets", "Investing", "StockMarket", "Options"
]
        
    
    
    def get_trends(self, limit=3): 
        trend_data = []               
        yield "<thinking>Searching ...</thinking>"
        for subreddit in self.subreddits:            
            trend_data += fetch_trends(subreddit, limit)            
        yield from self.llm.query_llm(trend_data)
        

        
        
