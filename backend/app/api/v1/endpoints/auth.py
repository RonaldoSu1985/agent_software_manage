from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.database import get_db
from app.models.user import User
from app.schemas.token import Token
from app.services.auth_service import verify_password, create_access_token

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    stmt = select(User).where(User.username == form_data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
