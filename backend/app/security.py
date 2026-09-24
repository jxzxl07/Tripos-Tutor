"""
Session tokens and the current-user dependency.

Flow: the frontend signs in with Google -> /api/auth/google verifies the Google
ID token -> we issue our OWN short-lived signed JWT. Every protected route
derives the user from that token, never from a user_id the client sends.
"""
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import User

ALGORITHM = "HS256"
TOKEN_TTL = timedelta(hours=12)

_bearer = HTTPBearer(auto_error=False)


def _unauthorized(detail: str = "Not authenticated") -> HTTPException:
    return HTTPException(401, detail, headers={"WWW-Authenticate": "Bearer"})


def create_access_token(user_id: int, now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    payload = {"sub": str(user_id), "iat": now, "exp": now + TOKEN_TTL}
    return jwt.encode(payload, settings.session_secret, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int:
    """Return the user id in a valid token, else raise 401.
    algorithms= is pinned, so an 'alg: none' or swapped-algorithm token is rejected."""
    try:
        payload = jwt.decode(token, settings.session_secret, algorithms=[ALGORITHM],
                             options={"require": ["exp", "sub"]})
        return int(payload["sub"])
    except (jwt.PyJWTError, ValueError):
        raise _unauthorized("Invalid or expired session")


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if creds is None:
        raise _unauthorized()
    user = db.get(User, decode_access_token(creds.credentials))
    if user is None:
        raise _unauthorized("User no longer exists")
    return user
