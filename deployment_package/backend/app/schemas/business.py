from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

# --- Base Schemas ---

class AgentBase(BaseModel):
    agent_code: str
    agent_name: str
    system_type: str

class Agent(AgentBase):
    id: int
    class Config:
        from_attributes = True

class SoftwareBase(BaseModel):
    name: str

class Software(SoftwareBase):
    id: int
    class Config:
        from_attributes = True

# --- Inventory Schemas ---

class InventoryBase(BaseModel):
    agent_id: int
    software_id: int
    quantity: int

class InventoryOut(InventoryBase):
    id: int
    agent: Agent
    software: Software
    updated_at: datetime
    class Config:
        from_attributes = True

class InventoryLogOut(BaseModel):
    id: int
    agent: Agent
    software: Software
    change_type: str
    before_qty: int
    change_qty: int
    after_qty: int
    related_id: Optional[int]
    operator_id: int
    created_at: datetime
    class Config:
        from_attributes = True

# --- Operation Schemas ---

class PurchaseCreate(BaseModel):
    system_type: str
    agent_code: str
    agent_name: str
    software_name: str
    quantity: int
    purchase_date: date = date.today()
    operator: Optional[str] = None
    remark: Optional[str] = None

class InstallationCreate(BaseModel):
    system_type: str
    agent_code: str
    agent_name: str
    software_name: str
    quantity: int
    merchant_code: str
    merchant_name: str
    install_date: date = date.today()
    remark: Optional[str] = None

class TransferCreate(BaseModel):
    from_system_type: str
    from_agent_code: str
    from_agent_name: str
    to_system_type: str
    to_agent_code: str
    to_agent_name: str
    software_name: str
    quantity: int
    transfer_date: date = date.today()
    operator: Optional[str] = None
    remark: Optional[str] = None
