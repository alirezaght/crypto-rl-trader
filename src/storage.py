from google.cloud import storage
from secret_manager import project_id
from firestore import get_cred
bucket_name = "tradepulse-bucket"

_client = None
def get_client():
    global _client
    if _client is None:
        _client = storage.Client(credentials=get_cred().get_credential())
    return _client

def upload_to_gcs(local_path: str, dest_path: str):
    bucket = get_client().bucket(bucket_name=bucket_name)
    blob = bucket.blob(dest_path)
    blob.upload_from_filename(local_path)
    
    
def download_from_gcs(remote_path: str, local_path: str):
    bucket = get_client().bucket(bucket_name=bucket_name)
    blob = bucket.blob(remote_path)
    blob.download_to_filename(local_path)
    

def gcs_file_exists(blob_name: str) -> bool:
    bucket = get_client().bucket(bucket_name=bucket_name)
    blob = bucket.blob(blob_name)
    return blob.exists()