import redis
import hashlib
import pickle
from secret_manager import get_redis_key

redis_key = get_redis_key().strip()

redis_client = redis.Redis(
    host='redis-19611.c327.europe-west1-2.gce.redns.redis-cloud.com',
    port=19611,
    decode_responses=False,
    username="default",
    password=redis_key,
)

def redis_cache(ttl=3600):  # TTL = 1 hour
    def decorator(func):
        def wrapper(*args, **kwargs):
            key_source = (func.__name__, args, kwargs)
            key = f"cache:{hashlib.md5(pickle.dumps(key_source)).hexdigest()}"

            cached = redis_client.get(key)
            if cached:
                return pickle.loads(cached)

            result = func(*args, **kwargs)
            redis_client.setex(key, ttl, pickle.dumps(result))
            return result
        return wrapper
    return decorator



