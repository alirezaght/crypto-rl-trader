import redis
import hashlib
import pickle
from utils.secret_manager import get_redis_key

_redis_client = None
_cache_available = True

def get_redis_client():
    global _redis_client
    if _cache_available is False:
        return None
    try:
        if _redis_client is None:
            redis_key = get_redis_key().strip()
            _redis_client = redis.Redis(
                host='redis-19611.c327.europe-west1-2.gce.redns.redis-cloud.com',
                port=19611,
                decode_responses=False,
                username="default",
                password=redis_key,
            )
            # _redis_client.flushdb()
    except Exception as e:
        print(f"Redis connection error: {e}")
        _redis_client = None
    if _redis_client is None:
        _cache_available = False
    return _redis_client


def redis_cache(ttl=3600):  # TTL = 1 hour
    def decorator(func):
        def wrapper(*args, **kwargs):
            if _cache_available:
                client = get_redis_client()
                key_source = (func.__name__, args, kwargs)
                key = f"cache:{hashlib.md5(pickle.dumps(key_source)).hexdigest()}"

                cached = client.get(key)
                if cached:
                    return pickle.loads(cached)

            result = func(*args, **kwargs)
            if _cache_available and client:
                client.setex(key, ttl, pickle.dumps(result))
            return result
        return wrapper
    return decorator



