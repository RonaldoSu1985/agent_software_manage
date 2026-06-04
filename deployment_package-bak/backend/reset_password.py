import asyncio
import sys
sys.path.append('.')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update
from app.core.config import settings
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def reset_admin_password():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        # 找到admin用户
        result = await session.execute(select(User).filter(User.username == 'admin'))
        user = result.scalar_one_or_none()
        
        if user:
            # 设置新密码
            new_password = "123456"
            hashed_password = pwd_context.hash(new_password)
            
            await session.execute(
                update(User)
                .where(User.username == 'admin')
                .values(hashed_password=hashed_password)
            )
            await session.commit()
            
            print(f"管理员密码已重置为: {new_password}")
            print(f"新哈希值: {hashed_password}")
        else:
            print("未找到admin用户")

if __name__ == "__main__":
    asyncio.run(reset_admin_password())
