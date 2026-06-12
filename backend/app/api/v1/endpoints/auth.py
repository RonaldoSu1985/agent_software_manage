from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.models.database import get_db
from app.models.user import User, Role
from app.schemas.token import LoginResponse
from app.services.auth_service import verify_password, create_access_token
from app.api.deps import get_current_user
import json
import uuid

router = APIRouter()

@router.get("/mcp-key")
async def get_mcp_key(current_user: User = Depends(get_current_user)):
    return {"mcp_key": current_user.mcp_key}

@router.post("/mcp-key")
async def generate_mcp_key(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_key = str(uuid.uuid4())
    current_user.mcp_key = new_key
    await db.commit()
    return {"mcp_key": new_key}

@router.post("/login", response_model=LoginResponse)
async def login(db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    stmt = select(User).options(joinedload(User.role)).where(User.username == form_data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    
    # 获取用户权限
    permissions = []
    if user.role and user.role.permissions:
        if isinstance(user.role.permissions, list):
            permissions = user.role.permissions
        else:
            try:
                permissions = json.loads(user.role.permissions)
            except:
                permissions = []
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "username": user.username,
        "full_name": user.full_name or user.username,
        "role_name": user.role.name if user.role else "",
        "permissions": permissions
    }
