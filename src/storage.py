from google.cloud import storage
from secret_manager import project_id
from firestore import cred
bucket_name = "tradepulse-bucket"
client = storage.Client(credentials=cred.get_credential())

def upload_to_gcs(local_path: str, dest_path: str):
    bucket = client.bucket(bucket_name=bucket_name)
    blob = bucket.blob(dest_path)
    blob.upload_from_filename(local_path)
    
    
def download_from_gcs(remote_path: str, local_path: str):
    bucket = client.bucket(bucket_name=bucket_name)
    blob = bucket.blob(remote_path)
    blob.download_to_filename(local_path)
    

def gcs_file_exists(blob_name: str) -> bool:
    bucket = client.bucket(bucket_name=bucket_name)
    blob = bucket.blob(blob_name)
    return blob.exists()