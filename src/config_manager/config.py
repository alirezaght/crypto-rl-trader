from db.firestore import get_db
from utils.redis_cache import redis_cache
from .schemas import Config, DBConfig
from typing import Literal
from base.schemas import MarketType

@redis_cache(3600 * 1)
def fetch_config() -> DBConfig:
    doc_ref = get_db().collection("config").document("default")
    doc = doc_ref.get()
    if not doc.exists:
        raise ValueError("No config document found in Firestore.")
    return DBConfig(**doc.to_dict())
    
# Should be separate because of the conflict between a decorator and Depends    
def get_db_config() -> DBConfig:    
    return fetch_config()


def get_config(type = MarketType) -> Config:    
    db_config = get_db_config()
    if type == "crypto":
        return Config(interval=db_config.INTERVAL,
                      symbols=db_config.PAIRS,
                      predict_days=db_config.PREDICT_DAYS,
                      window_days=db_config.WINDOW_DAYS)
    elif type == "stock":
        return Config(interval=db_config.INTERVAL_STOCK,
                      symbols=db_config.STOCKS,
                      predict_days=db_config.PREDICT_DAYS_STOCK,
                      window_days=db_config.WINDOW_DAYS_STOCK
                      )
