from fastapi import FastAPI
from fastapi.security import HTTPBearer
from src.routers import tiktok_router
from src.routers import llm_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.security import HTTPBearer
from src.routers import test_router
SECRET_KEY = "Yh2k7QSu4l8CZg5p6X3Pna9L0Miy4D3Bvt0JVr87UcOj69Kqw5R2Nmf4FWs03Hdx"
ALGORITHM = "HS256"
ISSUER = "https://account.biz5s.com"
AUDIENCE = "Tai Nguyen"

security = HTTPBearer()

# def is_token_expired(claims: dict) -> bool:
#     exp = claims.get("exp")
#     if exp is None:
#         return True  # treat as expired if no expiration
#     now = datetime.now(timezone.utc).timestamp()
#     return now >= exp

# def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
#     token = credentials.credentials
    
#     try:
#         payload = jwt.decode(
#             token,
#             SECRET_KEY,
#             algorithms=[ALGORITHM],
#             issuer=ISSUER,
#             audience=AUDIENCE
#         )
#         return payload
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")


app = FastAPI()

# @app.on_event("startup")
# def on_startup():
#     init_system_data()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(llm_router.router)
app.include_router(test_router.router)
app.include_router(tiktok_router.router)


# # === Protected route ===
# @app.get("/protected")
# async def protected(claims: dict = Depends(verify_jwt_token)):
#     if is_token_expired(claims):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token expired",
#         )

#     store = claims.get("store")   
#     user_id = claims.get("http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier")
#     role = claims.get("http://schemas.microsoft.com/ws/2008/06/identity/claims/role")
#     email = claims.get("http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress")
#     iss = claims.get("iss")

#     return {
#         "message": "✅ You are authorized!",
#         "claims": claims,
#         "store": store,
#         "user_id": user_id,
#         "role": role,
#         "email": email,
#         "iss": iss,
#     }