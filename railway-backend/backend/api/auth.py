from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.db.session import get_db
from backend.db.models import User
from backend.core.security import hash_password, verify_password, create_token
from backend.schemas.schemas import SignupRequest, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=TokenResponse)
async def signup(req: SignupRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")
    user = User(email=req.email, hashed_pwd=hash_password(req.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"access_token": create_token({"sub": str(user.id)})}

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.hashed_pwd):
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": create_token({"sub": str(user.id)})}
