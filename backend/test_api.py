import asyncio
import sys
sys.path.append('.')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.dictionary import DictionaryType, DictionaryItem
from sqlalchemy import select

async def test_dictionary_api():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        # 测试获取字典项列表
        print("测试获取字典项列表...")
        query = select(DictionaryItem).join(DictionaryType).order_by(DictionaryItem.sort_order, DictionaryItem.created_at)
        query = query.offset(0).limit(10)
        result = await session.execute(query)
        items = result.scalars().all()
        
        print(f"查询到 {len(items)} 条记录")
        for item in items:
            print(f"ID: {item.id}, Name: {item.item_name}, Key: {item.item_key}, Value: {item.item_value}")
        
        # 测试通过type_code过滤
        print("\n测试通过type_code过滤...")
        query = select(DictionaryItem).join(DictionaryType).filter(DictionaryType.type_code == 'SYSTEM_TYPE')
        result = await session.execute(query)
        items = result.scalars().all()
        print(f"SYSTEM_TYPE 类型下有 {len(items)} 条记录")

if __name__ == "__main__":
    asyncio.run(test_dictionary_api())
