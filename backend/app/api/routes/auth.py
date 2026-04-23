from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import jwt
import time
from app.core.config import settings

router = APIRouter()

class GoogleTokenRequest(BaseModel):
    credential: str  # the ID token from Google

@router.post("/auth/google")
def google_login(body: GoogleTokenRequest):
    try:
        id_info = id_token.verify_oauth2_token(
            body.credential,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    payload = {
        "sub": id_info["sub"],
        "email": id_info["email"],
        "name": id_info.get("name"),
        "picture": id_info.get("picture"),
        "exp": int(time.time()) + 60 * 60 * 24 * 7,  # 7 days
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return {"token": token, "user": payload}