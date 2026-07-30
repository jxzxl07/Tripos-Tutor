from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.db import SessionLocal
from app.models import User
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


class GoogleLoginRequest(BaseModel):
    credential: str          # the Google ID token from the frontend


@router.post("/google")
def google_login(req: GoogleLoginRequest):
    # 1. Verify the token is genuinely from Google and issued for our app
    try:
        info = id_token.verify_oauth2_token(
            req.credential,
            google_requests.Request(),
            settings.google_client_id,
        )
    except ValueError:
        raise HTTPException(401, "Invalid Google token")

    email = info.get("email")
    name = info.get("name", "")
    google_sub = info.get("sub")     # Google's unique user id

    # 2. (Optional) restrict to Cambridge — commented out so you can test with gmail.
    # if not email.endswith("@cam.ac.uk"):
    #     raise HTTPException(403, "Cambridge accounts only")

    # 3. Create or find the user
    s = SessionLocal()
    user = s.query(User).filter_by(google_sub=google_sub).first()
    if not user:
        user = User(google_sub=google_sub, email=email, name=name)
        s.add(user)
        s.commit()
        s.refresh(user)
    result = {"id": user.id, "email": user.email, "name": user.name}
    s.close()
    return result