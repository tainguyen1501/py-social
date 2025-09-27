import os
from datetime import datetime, timezone
from typing import Dict

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from src.routers.tiktok_router import create_tiktok_session
from src.routers import tiktok_router
from TikTokApi import TikTokApi

# === Security Config ===
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "Yh2k7QSu4l8CZg5p6X3Pna9L0Miy4D3Bvt0JVr87UcOj69Kqw5R2Nmf4FWs03Hdx"
)
ALGORITHM = "HS256"
ISSUER = "https://account.biz5s.com"
AUDIENCE = "Tai Nguyen"

security = HTTPBearer()


def is_token_expired(claims: dict) -> bool:
    exp = claims.get("exp")
    if exp is None:
        return True
    now = datetime.now(timezone.utc).timestamp()
    return now >= exp


def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=ISSUER,
            audience=AUDIENCE,
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# === FastAPI app ===
app = FastAPI(
    title="TikTok Downloader API",
    description="API service for downloading TikTok videos and trending feeds",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # update with specific domains if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Routers
app.include_router(tiktok_router.router)