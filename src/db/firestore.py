from firebase_admin import credentials, firestore
import firebase_admin


def init_firebase():
    firebase_admin.initialize_app(get_cred())

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
        _db = firestore.client() 
    return _db




