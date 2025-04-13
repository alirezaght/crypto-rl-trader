import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, Any


cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client() 

def fetch_config() -> Dict[str, Any]:
    doc_ref = db.collection("config").document("default")
    doc = doc_ref.get()
    if not doc.exists:
        raise ValueError("No config document found in Firestore.")
    return doc.to_dict()


def store_suggestion(pair: str, ip: str) -> None:
    suggestion_ref = db.collection("pair_suggestions").document()
    suggestion_ref.set({
        "pair": pair,
        "ip": ip,
        "timestamp": firestore.SERVER_TIMESTAMP
    })