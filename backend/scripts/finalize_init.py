import asyncio
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.database import Base
from app.models.user import User, Role
from app.models.business import Software
from app.core.config import settings

async def finalize_init():
    """完善初始化数据：更新管理员部门及初始化软件列表"""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        # 1. 更新 admin 用户
        result = await session.execute(
            select(User).filter(User.username == 'admin')
        )
        admin_user = result.scalar_one_or_none()
        
        if admin_user:
            admin_user.department = 'PRODUCT'
            admin_user.full_name = '系统管理员'
            await session.commit()
            print("已更新 admin 用户的部门为 PRODUCT，姓名为系统管理员")
        else:
            print("未找到 admin 用户")
            
        # 2. 初始化软件列表
        softwares = ['汇客餐饮', '汇客零售']
        for name in softwares:
            result = await session.execute(
                select(Software).filter(Software.name == name)
            )
            software = result.scalar_one_or_none()
            if not software:
                software = Software(name=name)
                session.add(software)
                print(f"已添加软件: {name}")
            else:
                print(f"软件已存在: {name}")
        await session.commit()

if __name__ == "__main__":
    asyncio.run(finalize_init())
    print("最终初始化完成")
