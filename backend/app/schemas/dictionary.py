from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class DictionaryTypeCreate(BaseModel):
    """创建字典类型"""
    type_name: str = Field(..., description="字典类型名称")
    type_code: str = Field(..., description="字典类型编码")
    description: Optional[str] = Field(None, description="描述")

class DictionaryTypeUpdate(BaseModel):
    """更新字典类型"""
    type_name: Optional[str] = Field(None, description="字典类型名称")
    description: Optional[str] = Field(None, description="描述")
    status: Optional[bool] = Field(None, description="状态")

class DictionaryTypeResponse(BaseModel):
    """字典类型响应"""
    id: int
    type_name: str
    type_code: str
    description: Optional[str]
    status: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DictionaryItemCreate(BaseModel):
    """创建字典项"""
    type_id: int = Field(..., description="字典类型ID")
    item_key: str = Field(..., description="字典KEY")
    item_value: str = Field(..., description="字典VALUE")
    item_name: str = Field(..., description="字典名称")
    sort_order: Optional[int] = Field(0, description="排序号")
    remark: Optional[str] = Field(None, description="备注")

class DictionaryItemUpdate(BaseModel):
    """更新字典项"""
    item_key: Optional[str] = Field(None, description="字典KEY")
    item_value: Optional[str] = Field(None, description="字典VALUE")
    item_name: Optional[str] = Field(None, description="字典名称")
    sort_order: Optional[int] = Field(None, description="排序号")
    status: Optional[bool] = Field(None, description="状态")
    remark: Optional[str] = Field(None, description="备注")

class DictionaryItemResponse(BaseModel):
    """字典项响应"""
    id: int
    type_id: int
    type_code: str
    type_name: str
    item_key: str
    item_value: str
    item_name: str
    sort_order: int
    status: bool
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DictionaryItemSimple(BaseModel):
    """字典项简单响应（用于下拉列表）"""
    item_key: str
    item_value: str
    item_name: str

    class Config:
        from_attributes = True

class DictionaryTypeListResponse(BaseModel):
    """字典类型列表响应"""
    total: int
    items: List[DictionaryTypeResponse]

class DictionaryItemListResponse(BaseModel):
    """字典项列表响应"""
    total: int
    items: List[DictionaryItemResponse]
