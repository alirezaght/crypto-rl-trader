from db.firestore import get_db
from utils.redis_cache import redis_cache
from .schemas import Config

@redis_cache(3600 * 1)
def fetch_config() -> Config:
    doc_ref = get_db().collection("config").document("default")
    doc = doc_ref.get()
    if not doc.exists:
        raise ValueError("No config document found in Firestore.")
    return Config(**doc.to_dict())

# Should be separate because of the conflict between a decorator and Depends
def get_config() -> Config:
    return fetch_config()
