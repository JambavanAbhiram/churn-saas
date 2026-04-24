from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from backend.core.config import get_settings

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(p: str) -> str:
    return pwd_ctx.hash(p)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)

def create_token(data: dict) -> str:
    s = get_settings()
    exp = datetime.utcnow() + timedelta(minutes=s.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({**data, "exp": exp}, s.SECRET_KEY, algorithm=s.ALGORITHM)

def decode_token(token: str) -> dict:
    s = get_settings()
    try:
        return jwt.decode(token, s.SECRET_KEY, algorithms=[s.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    uid = payload.get("sub")
    if uid is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return uid
