import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete
from app.models.database import Base
from app.models.dictionary import DictionaryType, DictionaryItem
from app.core.config import settings

async def init_dictionary():
    """初始化数据字典"""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        # 创建表
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # 创建代理商所属系统字典类型
        result = await session.execute(
            select(DictionaryType).filter(DictionaryType.type_code == 'SYSTEM_TYPE')
        )
        system_type = result.scalar_one_or_none()
        
        if not system_type:
            system_type = DictionaryType(
                type_name='代理商所属系统',
                type_code='SYSTEM_TYPE',
                description='代理商所属系统类型'
            )
            session.add(system_type)
            await session.commit()
            await session.refresh(system_type)
            print("已创建代理商所属系统字典类型")
        else:
            print("代理商所属系统字典类型已存在")
        
        # 删除旧的系统类型字典项
        await session.execute(
            delete(DictionaryItem).filter(DictionaryItem.type_id == system_type.id)
        )
        await session.commit()
        
        # 添加系统类型字典项
        system_items = [
            {'item_key': 'V3', 'item_value': 'V3系统', 'item_name': 'V3系统', 'sort_order': 1},
            {'item_key': 'LTB', 'item_value': 'LTB系统', 'item_name': 'LTB系统', 'sort_order': 2},
        ]
        for item in system_items:
            dict_item = DictionaryItem(
                type_id=system_type.id,
                **item
            )
            session.add(dict_item)
        await session.commit()
        print("已更新代理商所属系统字典项")
        
        # 创建软件名称字典类型
        result = await session.execute(
            select(DictionaryType).filter(DictionaryType.type_code == 'SOFTWARE_NAME')
        )
        software_type = result.scalar_one_or_none()
        
        if not software_type:
            software_type = DictionaryType(
                type_name='软件名称',
                type_code='SOFTWARE_NAME',
                description='软件名称列表'
            )
            session.add(software_type)
            await session.commit()
            await session.refresh(software_type)
            print("已创建软件名称字典类型")
        else:
            print("软件名称字典类型已存在")
        
        # 删除旧的软件名称字典项
        await session.execute(
            delete(DictionaryItem).filter(DictionaryItem.type_id == software_type.id)
        )
        await session.commit()
        
        # 添加软件名称字典项
        software_items = [
            {'item_key': 'HK_CY', 'item_value': '汇客餐饮', 'item_name': '汇客餐饮', 'sort_order': 1},
            {'item_key': 'HK_LS', 'item_value': '汇客零售', 'item_name': '汇客零售', 'sort_order': 2},
        ]
        for item in software_items:
            dict_item = DictionaryItem(
                type_id=software_type.id,
                **item
            )
            session.add(dict_item)
        await session.commit()
        print("已更新软件名称字典项")

if __name__ == "__main__":
    asyncio.run(init_dictionary())
    print("数据字典初始化完成")