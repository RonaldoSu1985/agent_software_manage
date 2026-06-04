import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.database import Base
from app.core.config import settings

# 必须导入所有模型类以确保它们被注册到Base.metadata
from app.models.user import User, Role
from app.models.business import Agent, Software, Inventory, PurchaseRecord, InstallationRecord, TransferRecord, InventoryLog
from app.models.dictionary import DictionaryType, DictionaryItem

async def init_database():
    """初始化数据库表结构"""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
        print("所有表创建成功！")

if __name__ == "__main__":
    asyncio.run(init_database())
    print("数据库初始化完成")
