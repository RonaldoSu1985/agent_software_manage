from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.database import Base

class DictionaryType(Base):
    """数据字典类型表"""
    __tablename__ = "dictionary_type"
    
    id = Column(Integer, primary_key=True, index=True)
    type_name = Column(String(100), nullable=False, comment="字典类型名称")
    type_code = Column(String(50), nullable=False, unique=True, comment="字典类型编码")
    description = Column(String(500), comment="描述")
    status = Column(Boolean, default=True, comment="状态：True启用，False禁用")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    items = relationship("DictionaryItem", back_populates="type")

class DictionaryItem(Base):
    """数据字典项表"""
    __tablename__ = "dictionary_item"
    
    id = Column(Integer, primary_key=True, index=True)
    type_id = Column(Integer, ForeignKey("dictionary_type.id"), nullable=False, comment="字典类型ID")
    item_key = Column(String(100), nullable=False, comment="字典KEY")
    item_value = Column(String(255), nullable=False, comment="字典VALUE")
    item_name = Column(String(100), nullable=False, comment="字典名称")
    sort_order = Column(Integer, default=0, comment="排序号")
    status = Column(Boolean, default=True, comment="状态：True启用，False禁用")
    remark = Column(String(500), comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    type = relationship("DictionaryType", back_populates="items")
