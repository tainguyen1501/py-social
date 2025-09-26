import os
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timezone
from typing import Dict

SECRET_KEY = os.getenv("SECRET_KEY") or "Yh2k7QSu4l8CZg5p6X3Pna9L0Miy4D3Bvt0JVr87UcOj69Kqw5R2Nmf4FWs03Hdx"
ALGORITHM = os.getenv("ALGORITHM") or "HS256"
ISSUER = os.getenv("ISSUER") or "https://account.biz5s.com"
AUDIENCE = os.getenv("AUDIENCE") or "Tai Nguyen"

security = HTTPBearer()

def is_token_expired(claims: dict) -> bool:
    exp = claims.get("exp")
    if exp is None:
        return True  # treat as expired if no expiration
    now = datetime.now(timezone.utc).timestamp()
    return now >= exp

def get_claims(request: Request):
    return request.state.claims

def get_store_id(request: Request) -> str | None:
    return request.state.claims.get("store")

def verify_jwt_token( request: Request,credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=ISSUER,
            audience=AUDIENCE
        )

         # Optional expiration check
        if is_token_expired(payload):
            raise HTTPException(status_code=401, detail="Token expired")

        # Store claims on the request
        request.state.claims = payload

        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")