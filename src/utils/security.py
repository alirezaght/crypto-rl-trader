from fastapi import Depends, HTTPException
from firebase_admin import auth as firebase_auth
from base.middleware.request import get_current_request

def get_current_user():
    request = get_current_request()
    if request is None:
        raise HTTPException(status_code=401, detail="Request context not found")
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = auth_header.split("Bearer ")[1]
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")