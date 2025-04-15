from google.cloud import secretmanager
from firestore import cred
project_id = "silver-treat-456607-e6"

client = secretmanager.SecretManagerServiceClient(credentials=cred.get_credential())


def get_secret(secret_name):
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def get_cryptopanic_key():
    return get_secret("cryptopanic-api")

def get_groq_key():
    return get_secret("groq-api")

def get_redis_key():
    return get_secret("redis-secret")

