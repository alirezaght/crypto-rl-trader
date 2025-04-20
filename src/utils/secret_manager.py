from google.cloud import secretmanager
from db.firestore import get_cred
project_id = "silver-treat-456607-e6"

_client = None

def get_client():
    global _client
    if _client is None:
        _client = secretmanager.SecretManagerServiceClient(credentials=get_cred().get_credential())
    return _client

def get_secret(secret_name):
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = get_client().access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8").strip()


def get_cryptopanic_key():
    return get_secret("cryptopanic-api")

def get_groq_key():
    return get_secret("groq-api")

def get_redis_key():
    return get_secret("redis-secret")

