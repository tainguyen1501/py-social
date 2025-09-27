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
SECRET_KEY = "Yh2k7QSu4l8CZg5p6X3Pna9L0Miy4D3Bvt0JVr87UcOj69Kqw5R2Nmf4FWs03Hdx"
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
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup / Shutdown events
@app.on_event("startup")
async def startup_event():
    api = await create_tiktok_session()
    app.state.tiktok_api = api
    print("✅ TikTok session initialized")

@app.on_event("shutdown")
async def shutdown_event():
    api: TikTokApi = getattr(app.state, "tiktok_api", None) # type: ignore
    if api:
        await api.close_sessions()
        print("🛑 TikTok session closed")

# Routers
app.include_router(tiktok_router.router)

# Example protected route
@app.get("/protected")
async def protected(claims: dict = Depends(verify_jwt_token)):
    if is_token_expired(claims):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    return {
        "message": "✅ You are authorized!",
        "claims": claims,
    }
