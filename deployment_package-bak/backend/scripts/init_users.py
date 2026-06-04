import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.database import Base
from app.models.user import User, Role
from app.core.config import settings
from app.services.auth_service import get_password_hash

async def init_users():
    """初始化用户和角色"""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # 创建管理员角色
        result = await session.execute(
            select(Role).filter(Role.name == 'admin')
        )
        admin_role = result.scalar_one_or_none()
        
        if not admin_role:
            admin_role = Role(
                name='admin',
                permissions=json.dumps(['*'])
            )
            session.add(admin_role)
            await session.commit()
            await session.refresh(admin_role)
            print("已创建管理员角色")
        else:
            print("管理员角色已存在")
        
        # 创建admin用户
        result = await session.execute(
            select(User).filter(User.username == 'admin')
        )
        admin_user = result.scalar_one_or_none()
        
        if not admin_user:
            admin_user = User(
                username='admin',
                hashed_password=get_password_hash('123456'),
                full_name='管理员',
                role_id=admin_role.id,
                is_active=True
            )
            session.add(admin_user)
            await session.commit()
            print("已创建admin用户")
        else:
            print("admin用户已存在")

if __name__ == "__main__":
    import json
    asyncio.run(init_users())
    print("用户初始化完成")
