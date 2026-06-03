from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List
from app.models.database import get_db
from app.models.user import User, Role
from app.schemas.user import UserCreate, UserUpdate, UserResponse, RoleCreate, RoleUpdate, RoleResponse
from app.services.auth_service import get_password_hash
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
async def get_users(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(select(User).options(joinedload(User.role)))
    users = result.scalars().all()
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            role_id=user.role_id,
            role_name=user.role.name if user.role else "",
            is_active=user.is_active
        ) for user in users
    ]

@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(select(User).where(User.username == user.username))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role_id=user.role_id,
        is_active=user.is_active
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    role = await db.get(Role, user.role_id)
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        full_name=new_user.full_name,
        role_id=new_user.role_id,
        role_name=role.name if role else "",
        is_active=new_user.is_active
    )

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserUpdate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    db_user = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    
    if user.username and user.username != db_user.username:
        result = await db.execute(select(User).where(User.username == user.username))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
        db_user.username = user.username
    
    if user.password:
        db_user.hashed_password = get_password_hash(user.password)
    
    if user.full_name:
        db_user.full_name = user.full_name
    
    if user.role_id is not None:
        db_user.role_id = user.role_id
    
    if user.is_active is not None:
        db_user.is_active = user.is_active
    
    await db.commit()
    await db.refresh(db_user)
    
    role = await db.get(Role, db_user.role_id)
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        full_name=db_user.full_name,
        role_id=db_user.role_id,
        role_name=role.name if role else "",
        is_active=db_user.is_active
    )

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    db_user = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    
    await db.delete(db_user)
    await db.commit()
    return {"message": "用户删除成功"}

@router.get("/roles")
async def get_roles(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(select(Role))
    roles = result.scalars().all()
    import json
    return [
        {
            "id": role.id,
            "name": role.name,
            "permissions": role.permissions if isinstance(role.permissions, list) else (json.loads(role.permissions) if role.permissions else [])
        } for role in roles
    ]

@router.post("/roles", response_model=RoleResponse)
async def create_role(role: RoleCreate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(select(Role).where(Role.name == role.name))
    existing_role = result.scalar_one_or_none()
    if existing_role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="角色名称已存在")
    
    new_role = Role(name=role.name, permissions=role.permissions)
    db.add(new_role)
    await db.commit()
    await db.refresh(new_role)
    return new_role

@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(role_id: int, role: RoleUpdate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    db_role = await db.get(Role, role_id)
    if not db_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    
    if role.name and role.name != db_role.name:
        result = await db.execute(select(Role).where(Role.name == role.name))
        existing_role = result.scalar_one_or_none()
        if existing_role:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="角色名称已存在")
        db_role.name = role.name
    
    if role.permissions is not None:
        db_role.permissions = role.permissions
    
    await db.commit()
    await db.refresh(db_role)
    return db_role

@router.delete("/roles/{role_id}")
async def delete_role(role_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    db_role = await db.get(Role, role_id)
    if not db_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    
    result = await db.execute(select(User).where(User.role_id == role_id))
    users_with_role = result.scalars().first()
    if users_with_role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该角色下还有用户，无法删除")
    
    await db.delete(db_role)
    await db.commit()
    return {"message": "角色删除成功"}