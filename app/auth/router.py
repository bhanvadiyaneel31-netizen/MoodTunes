from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.schemas import UserCreate, UserLogin, TokenPair, TokenRefresh, UserResponse
from app.auth.service import create_user, authenticate_user
from app.auth.dependencies import get_current_user
from app.auth.utils import create_access_token, create_refresh_token, decode_token
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, data)


@router.post("/login", response_model=TokenPair)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, data.email, data.password)
    return _generate_tokens(user)


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    payload = decode_token(data.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    from app.auth.service import get_user_by_id
    import uuid
    user = await get_user_by_id(db, uuid.UUID(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    return _generate_tokens(user)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


def _generate_tokens(user: User) -> TokenPair:
    payload = {"sub": str(user.id), "username": user.username}
    return TokenPair(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload),
    )
