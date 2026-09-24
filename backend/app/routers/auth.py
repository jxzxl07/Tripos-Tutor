from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.db import get_db
from app.models import User
from app.config import settings
from app.security import create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


class GoogleLoginRequest(BaseModel):
    credential: str          # the Google ID token from the frontend


@router.post("/google")
def google_login(req: GoogleLoginRequest, db: Session = Depends(get_db)):
    # Verify the token is genuinely from Google and issued for our app
    try:
        info = id_token.verify_oauth2_token(
            req.credential,
            google_requests.Request(),
            settings.google_client_id,
        )
    except ValueError:
        raise HTTPException(401, "Invalid Google token")

    email = (info.get("email") or "").lower()
    name = info.get("name", "")
    google_sub = info.get("sub")     # Google's unique user id

    # Only accept a verified Cambridge address (email may be missing/unverified)
    if not info.get("email_verified") or not email.endswith("@cam.ac.uk"):
        raise HTTPException(403, "Cambridge accounts only")

    # Create or find the user
    user = db.query(User).filter_by(google_sub=google_sub).first()
    if not user:
        user = User(google_sub=google_sub, email=email, name=name)
        db.add(user)
        db.commit()
        db.refresh(user)

    # From here on the client proves who it is with OUR signed token,
    # not by sending a user_id we would have to trust.
    return {
        "token": create_access_token(user.id),
        "user": {"id": user.id, "email": user.email, "name": user.name},
    }
