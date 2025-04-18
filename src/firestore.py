import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, Any

_cred = None

def get_cred():
    global _cred
    if _cred is None:
        _cred = credentials.Certificate("./serviceAccountKey.json")
    return _cred

_db = None
def get_db():
    global _db
    if _db is None:        
        firebase_admin.initialize_app(get_cred())
        _db = firestore.client() 
    return _db

def fetch_config() -> Dict[str, Any]:
    doc_ref = get_db().collection("config").document("default")
    doc = doc_ref.get()
    if not doc.exists:
        raise ValueError("No config document found in Firestore.")
    return doc.to_dict()


def store_suggestion(pair: str, ip: str) -> None:
    suggestion_ref = get_db().collection("pair_suggestions").document()
    suggestion_ref.set({
        "pair": pair,
        "ip": ip,
        "timestamp": firestore.SERVER_TIMESTAMP
    })