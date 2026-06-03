import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.database import Base
from app.models.business import Agent, Software, Inventory, PurchaseRecord, InstallationRecord, TransferRecord, InventoryLog
from app.models.dictionary import DictionaryType, DictionaryItem
from app.core.config import settings

async def clear_test_data():
    """清空测试数据（保留用户和角色）"""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        # 需要清空的表（按外键依赖顺序）
        tables_to_clear = [
            InventoryLog,
            TransferRecord,
            InstallationRecord,
            PurchaseRecord,
            Inventory,
            Software,
            Agent,
            DictionaryItem,
            DictionaryType,
        ]
        
        for table in tables_to_clear:
            await session.execute(table.__table__.delete())
            print(f"已清空表: {table.__tablename__}")
        
        await session.commit()
        print("\n测试数据清空完成！")

if __name__ == "__main__":
    asyncio.run(clear_test_data())
