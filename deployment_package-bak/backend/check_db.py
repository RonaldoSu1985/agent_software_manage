import asyncio
import sys
sys.path.append('.')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.database import Base
from app.models.dictionary import DictionaryType, DictionaryItem
from app.core.config import settings

async def check_data():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        
        # 查询字典类型
        types_result = await session.execute(select(DictionaryType))
        types = types_result.scalars().all()
        print(f"字典类型数量: {len(types)}")
        for t in types:
            print(f"  - {t.id}: {t.type_name} ({t.type_code})")
        
        # 查询字典项
        items_result = await session.execute(select(DictionaryItem))
        items = items_result.scalars().all()
        print(f"\n字典项数量: {len(items)}")
        for item in items:
            print(f"  - {item.id}: {item.item_name} (type_id={item.type_id})")

if __name__ == "__main__":
    asyncio.run(check_data())
