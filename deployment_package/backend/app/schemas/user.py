from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    role_id: int
    is_active: bool = True
    department: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    department: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    role_id: Optional[int] = None
    role_name: str
    is_active: bool
    department: str
    department_name: str

class RoleCreate(BaseModel):
    name: str
    permissions: List[str] = []

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    permissions: Optional[List[str]] = None

class RoleResponse(BaseModel):
    id: int
    name: str
    permissions: List[str]

    class Config:
        from_attributes = True