from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.models.database import get_db
from app.crud.dictionary import (
    create_dictionary_type, get_dictionary_type, get_dictionary_types,
    get_dictionary_types_count, update_dictionary_type, delete_dictionary_type,
    create_dictionary_item, get_dictionary_item, get_dictionary_items,
    get_dictionary_items_count, get_dictionary_items_by_type_code,
    update_dictionary_item, delete_dictionary_item, get_dictionary_type_by_code
)
from app.schemas.dictionary import (
    DictionaryTypeCreate, DictionaryTypeUpdate, DictionaryTypeResponse,
    DictionaryTypeListResponse, DictionaryItemCreate, DictionaryItemUpdate,
    DictionaryItemResponse, DictionaryItemListResponse, DictionaryItemSimple
)
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

# ========== 字典类型 API ==========

@router.post("/types", response_model=DictionaryTypeResponse, summary="创建字典类型")
async def create_type(
    schema: DictionaryTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_type = await get_dictionary_type_by_code(db, schema.type_code)
    if existing_type:
        raise HTTPException(status_code=400, detail="字典类型编码已存在")
    return await create_dictionary_type(db, schema)

@router.get("/types/{type_id}", response_model=DictionaryTypeResponse, summary="获取字典类型详情")
async def get_type(
    type_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_type = await get_dictionary_type(db, type_id)
    if not db_type:
        raise HTTPException(status_code=404, detail="字典类型不存在")
    return db_type

@router.get("/types", response_model=DictionaryTypeListResponse, summary="获取字典类型列表")
async def list_types(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    type_name: Optional[str] = Query(None),
    type_code: Optional[str] = Query(None),
    status: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    skip = (page - 1) * page_size
    items = await get_dictionary_types(db, skip=skip, limit=page_size, 
                                       type_name=type_name, type_code=type_code, status=status)
    total = await get_dictionary_types_count(db, type_name=type_name, type_code=type_code, status=status)
    return {"total": total, "items": items}

@router.put("/types/{type_id}", response_model=DictionaryTypeResponse, summary="更新字典类型")
async def update_type(
    type_id: int,
    schema: DictionaryTypeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_type = await get_dictionary_type(db, type_id)
    if not db_type:
        raise HTTPException(status_code=404, detail="字典类型不存在")
    return await update_dictionary_type(db, type_id, schema)

@router.delete("/types/{type_id}", summary="删除字典类型")
async def delete_type(
    type_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = await delete_dictionary_type(db, type_id)
    if not success:
        raise HTTPException(status_code=404, detail="字典类型不存在")
    return {"message": "删除成功"}

# ========== 字典项 API ==========

@router.post("/items", response_model=DictionaryItemResponse, summary="创建字典项")
async def create_item(
    schema: DictionaryItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_type = await get_dictionary_type(db, schema.type_id)
    if not db_type:
        raise HTTPException(status_code=400, detail="字典类型不存在")
    
    # 检查同一类型下是否存在相同的item_key
    items = await get_dictionary_items(db, type_id=schema.type_id, item_key=schema.item_key)
    if items:
        raise HTTPException(status_code=400, detail="同一类型下字典KEY已存在")
    
    item = await create_dictionary_item(db, schema)
    # 补充type_code和type_name
    return {
        **item.__dict__,
        "type_code": db_type.type_code,
        "type_name": db_type.type_name
    }

@router.get("/items", response_model=DictionaryItemListResponse, summary="获取字典项列表")
async def list_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    type_id: Optional[int] = Query(None),
    type_code: Optional[str] = Query(None),
    item_name: Optional[str] = Query(None),
    item_key: Optional[str] = Query(None),
    status: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    skip = (page - 1) * page_size
    items = await get_dictionary_items(db, skip=skip, limit=page_size,
                                       type_id=type_id, type_code=type_code,
                                       item_name=item_name, item_key=item_key, status=status)
    total = await get_dictionary_items_count(db, type_id=type_id, type_code=type_code,
                                             item_name=item_name, item_key=item_key, status=status)
    
    result_items = []
    for item in items:
        db_type = await get_dictionary_type(db, item.type_id)
        result_items.append({
            **item.__dict__,
            "type_code": db_type.type_code if db_type else "",
            "type_name": db_type.type_name if db_type else ""
        })
    
    return {"total": total, "items": result_items}

# ========== 导出 API ==========

@router.get("/items/export", summary="导出字典项")
async def export_items(
    type_code: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items = await get_dictionary_items(db, type_code=type_code, status=True)
    
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["字典编号", "字典名称", "字典类型", "字典KEY", "字典VALUE", "状态", "备注", "创建时间"])
    
    for item in items:
        db_type = await get_dictionary_type(db, item.type_id)
        writer.writerow([
            item.id,
            item.item_name,
            db_type.type_name if db_type else "",
            item.item_key,
            item.item_value,
            "启用" if item.status else "禁用",
            item.remark or "",
            item.created_at.strftime("%Y-%m-%d %H:%M:%S")
        ])
    
    output.seek(0)
    from fastapi.responses import PlainTextResponse
    import urllib.parse
    filename = urllib.parse.quote(f"字典数据_{type_code or 'all'}.csv")
    return PlainTextResponse(
        content=output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}; filename*=UTF-8''{filename}"}
    )

@router.get("/items/{item_id}", response_model=DictionaryItemResponse, summary="获取字典项详情")
async def get_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = await get_dictionary_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="字典项不存在")
    
    db_type = await get_dictionary_type(db, db_item.type_id)
    return {
        **db_item.__dict__,
        "type_code": db_type.type_code if db_type else "",
        "type_name": db_type.type_name if db_type else ""
    }

@router.put("/items/{item_id}", response_model=DictionaryItemResponse, summary="更新字典项")
async def update_item(
    item_id: int,
    schema: DictionaryItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = await get_dictionary_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="字典项不存在")
    
    updated_item = await update_dictionary_item(db, item_id, schema)
    
    db_type = await get_dictionary_type(db, updated_item.type_id)
    return {
        **updated_item.__dict__,
        "type_code": db_type.type_code if db_type else "",
        "type_name": db_type.type_name if db_type else ""
    }

@router.delete("/items/{item_id}", summary="删除字典项")
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = await delete_dictionary_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="字典项不存在")
    return {"message": "删除成功"}

# ========== 下拉列表 API ==========

@router.get("/items/by-type/{type_code}", response_model=List[DictionaryItemSimple], summary="根据类型编码获取字典项（用于下拉列表）")
async def get_items_by_type_code(
    type_code: str,
    db: AsyncSession = Depends(get_db)
):
    items = await get_dictionary_items_by_type_code(db, type_code)
    return items