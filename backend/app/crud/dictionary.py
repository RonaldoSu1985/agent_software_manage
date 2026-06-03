from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, desc, or_, func
from typing import Optional, List
from app.models.dictionary import DictionaryType, DictionaryItem
from app.schemas.dictionary import DictionaryTypeCreate, DictionaryTypeUpdate, DictionaryItemCreate, DictionaryItemUpdate

# ========== 字典类型 CRUD ==========

async def create_dictionary_type(db: AsyncSession, schema: DictionaryTypeCreate) -> DictionaryType:
    """创建字典类型"""
    db_type = DictionaryType(
        type_name=schema.type_name,
        type_code=schema.type_code,
        description=schema.description
    )
    db.add(db_type)
    await db.commit()
    await db.refresh(db_type)
    return db_type

async def get_dictionary_type(db: AsyncSession, type_id: int) -> Optional[DictionaryType]:
    """根据ID获取字典类型"""
    result = await db.execute(select(DictionaryType).filter(DictionaryType.id == type_id))
    return result.scalar_one_or_none()

async def get_dictionary_type_by_code(db: AsyncSession, type_code: str) -> Optional[DictionaryType]:
    """根据编码获取字典类型"""
    result = await db.execute(select(DictionaryType).filter(DictionaryType.type_code == type_code))
    return result.scalar_one_or_none()

async def get_dictionary_types(db: AsyncSession, skip: int = 0, limit: int = 10, 
                               type_name: Optional[str] = None, type_code: Optional[str] = None,
                               status: Optional[bool] = None) -> List[DictionaryType]:
    """获取字典类型列表"""
    query = select(DictionaryType).order_by(desc(DictionaryType.created_at))
    
    if type_name:
        query = query.filter(DictionaryType.type_name.ilike(f"%{type_name}%"))
    if type_code:
        query = query.filter(DictionaryType.type_code.ilike(f"%{type_code}%"))
    if status is not None:
        query = query.filter(DictionaryType.status == status)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_dictionary_types_count(db: AsyncSession, type_name: Optional[str] = None, 
                                     type_code: Optional[str] = None, 
                                     status: Optional[bool] = None) -> int:
    """获取字典类型总数"""
    query = select(func.count(DictionaryType.id))
    
    if type_name:
        query = query.filter(DictionaryType.type_name.ilike(f"%{type_name}%"))
    if type_code:
        query = query.filter(DictionaryType.type_code.ilike(f"%{type_code}%"))
    if status is not None:
        query = query.filter(DictionaryType.status == status)
    
    result = await db.execute(query)
    return result.scalar_one()

async def update_dictionary_type(db: AsyncSession, type_id: int, schema: DictionaryTypeUpdate) -> Optional[DictionaryType]:
    """更新字典类型"""
    update_data = schema.dict(exclude_unset=True)
    if update_data:
        await db.execute(
            update(DictionaryType)
            .where(DictionaryType.id == type_id)
            .values(**update_data)
        )
        await db.commit()
    
    return await get_dictionary_type(db, type_id)

async def delete_dictionary_type(db: AsyncSession, type_id: int) -> bool:
    """删除字典类型"""
    result = await db.execute(delete(DictionaryType).where(DictionaryType.id == type_id))
    await db.commit()
    return result.rowcount > 0

# ========== 字典项 CRUD ==========

async def create_dictionary_item(db: AsyncSession, schema: DictionaryItemCreate) -> DictionaryItem:
    """创建字典项"""
    db_item = DictionaryItem(
        type_id=schema.type_id,
        item_key=schema.item_key,
        item_value=schema.item_value,
        item_name=schema.item_name,
        sort_order=schema.sort_order,
        remark=schema.remark
    )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def get_dictionary_item(db: AsyncSession, item_id: int) -> Optional[DictionaryItem]:
    """根据ID获取字典项"""
    result = await db.execute(select(DictionaryItem).filter(DictionaryItem.id == item_id))
    return result.scalar_one_or_none()

async def get_dictionary_items(db: AsyncSession, skip: int = 0, limit: int = 10,
                               type_id: Optional[int] = None, type_code: Optional[str] = None,
                               item_name: Optional[str] = None, item_key: Optional[str] = None,
                               status: Optional[bool] = None) -> List[DictionaryItem]:
    """获取字典项列表"""
    query = select(DictionaryItem).join(DictionaryType).order_by(DictionaryItem.sort_order, DictionaryItem.created_at)
    
    if type_id:
        query = query.filter(DictionaryItem.type_id == type_id)
    if type_code:
        query = query.filter(DictionaryType.type_code == type_code)
    if item_name:
        query = query.filter(DictionaryItem.item_name.ilike(f"%{item_name}%"))
    if item_key:
        query = query.filter(DictionaryItem.item_key.ilike(f"%{item_key}%"))
    if status is not None:
        query = query.filter(DictionaryItem.status == status)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_dictionary_items_count(db: AsyncSession, type_id: Optional[int] = None, 
                                     type_code: Optional[str] = None,
                                     item_name: Optional[str] = None, 
                                     item_key: Optional[str] = None,
                                     status: Optional[bool] = None) -> int:
    """获取字典项总数"""
    query = select(func.count(DictionaryItem.id)).select_from(DictionaryItem).join(DictionaryType)
    
    if type_id:
        query = query.filter(DictionaryItem.type_id == type_id)
    if type_code:
        query = query.filter(DictionaryType.type_code == type_code)
    if item_name:
        query = query.filter(DictionaryItem.item_name.ilike(f"%{item_name}%"))
    if item_key:
        query = query.filter(DictionaryItem.item_key.ilike(f"%{item_key}%"))
    if status is not None:
        query = query.filter(DictionaryItem.status == status)
    
    result = await db.execute(query)
    return result.scalar_one()

async def get_dictionary_items_by_type_code(db: AsyncSession, type_code: str) -> List[DictionaryItem]:
    """根据类型编码获取启用的字典项列表"""
    query = select(DictionaryItem).join(DictionaryType).filter(
        DictionaryType.type_code == type_code,
        DictionaryItem.status == True,
        DictionaryType.status == True
    ).order_by(DictionaryItem.sort_order)
    
    result = await db.execute(query)
    return result.scalars().all()

async def update_dictionary_item(db: AsyncSession, item_id: int, schema: DictionaryItemUpdate) -> Optional[DictionaryItem]:
    """更新字典项"""
    update_data = schema.dict(exclude_unset=True)
    if update_data:
        await db.execute(
            update(DictionaryItem)
            .where(DictionaryItem.id == item_id)
            .values(**update_data)
        )
        await db.commit()
    
    return await get_dictionary_item(db, item_id)

async def delete_dictionary_item(db: AsyncSession, item_id: int) -> bool:
    """删除字典项"""
    result = await db.execute(delete(DictionaryItem).where(DictionaryItem.id == item_id))
    await db.commit()
    return result.rowcount > 0
