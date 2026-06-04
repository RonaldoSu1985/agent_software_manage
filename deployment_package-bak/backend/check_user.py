import asyncio
import sys
sys.path.append('.')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.core.config import settings
from app.models.user import User

async def check_users():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"用户数量: {len(users)}")
        for user in users:
            print(f"ID: {user.id}, 用户名: {user.username}, 密码: {user.hashed_password}, 角色ID: {user.role_id}")

if __name__ == "__main__":
    asyncio.run(check_users())
