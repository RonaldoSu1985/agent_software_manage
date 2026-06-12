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
        
        # 创建部门字典类型
        result = await session.execute(
            select(DictionaryType).filter(DictionaryType.type_code == 'DEPARTMENT')
        )
        department_type = result.scalar_one_or_none()
        
        if not department_type:
            department_type = DictionaryType(
                type_name='部门',
                type_code='DEPARTMENT',
                description='部门列表'
            )
            session.add(department_type)
            await session.commit()
            await session.refresh(department_type)
            print("已创建部门字典类型")
        else:
            print("部门字典类型已存在")
        
        # 删除旧的部门字典项
        await session.execute(
            delete(DictionaryItem).filter(DictionaryItem.type_id == department_type.id)
        )
        await session.commit()
        
        # 添加部门字典项
        department_items = [
            {'item_key': 'PRODUCT', 'item_value': '产品项目部', 'item_name': '产品项目部', 'sort_order': 1},
            {'item_key': 'QUALITY', 'item_value': '测试部', 'item_name': '测试部', 'sort_order': 2},
            {'item_key': 'TECH', 'item_value': '技术部', 'item_name': '技术部', 'sort_order': 3},
            {'item_key': 'MANAGEMENT', 'item_value': '运维部', 'item_name': '运维部', 'sort_order': 4},
            {'item_key': 'OPERATIONS', 'item_value': '运营部', 'item_name': '运营部', 'sort_order': 5},
            {'item_key': 'CUSTOMER_SERVICE', 'item_value': '服务部', 'item_name': '服务部', 'sort_order': 6},
            {'item_key': 'FINANCE', 'item_value': '财务部', 'item_name': '财务部', 'sort_order': 7},
            {'item_key': 'FINANCE', 'item_value': '核算部', 'item_name': '核算部', 'sort_order': 8},
            {'item_key': 'PURCHASE', 'item_value': '采购部', 'item_name': '采购部', 'sort_order': 9},
            {'item_key': 'PURCHASE', 'item_value': '仓储部', 'item_name': '仓储部', 'sort_order': 10},
            {'item_key': 'BUSINESS', 'item_value': '风控部', 'item_name': '风控部', 'sort_order': 11},
            {'item_key': 'SUPPORT', 'item_value': '金融合作部', 'item_name': '金融合作部', 'sort_order': 12},
            {'item_key': 'SALES', 'item_value': '销售部', 'item_name': '销售部', 'sort_order': 13},
            {'item_key': 'MARKETING', 'item_value': '市场品牌部', 'item_name': '市场品牌部', 'sort_order': 14},
            {'item_key': 'MARKETING', 'item_value': '创新事业部', 'item_name': '创新事业部', 'sort_order': 15},
            {'item_key': 'HR', 'item_value': '人力资源部', 'item_name': '人力资源部', 'sort_order': 16},
        ]
        for item in department_items:
            dict_item = DictionaryItem(
                type_id=department_type.id,
                **item
            )
            session.add(dict_item)
        await session.commit()
        print("已更新部门字典项")

if __name__ == "__main__":
    asyncio.run(init_dictionary())
    print("数据字典初始化完成")