from google.cloud import secretmanager
from firestore import cred
project_id = "silver-treat-456607-e6"

client = secretmanager.SecretManagerServiceClient(credentials=cred.get_credential())

def get_twelvedata_key():    
    name = f"projects/{project_id}/secrets/twelvedata-api-key/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")