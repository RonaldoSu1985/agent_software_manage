from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, case
from sqlalchemy.orm import joinedload
from typing import List, Optional
from app.models.database import get_db
from app.models.business import Inventory, InventoryLog, Agent, Software, TransferRecord, InstallationRecord
from app.schemas.business import InventoryOut, InventoryLogOut
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/list", response_model=List[InventoryOut])
async def list_inventory(
    db: AsyncSession = Depends(get_db),
    system_type: Optional[str] = Query(None),
    agent_code: Optional[str] = Query(None),
    agent_name: Optional[str] = Query(None),
    software_name: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Inventory).options(
        joinedload(Inventory.agent),
        joinedload(Inventory.software)
    ).join(Inventory.agent).join(Inventory.software)
    
    if system_type:
        stmt = stmt.where(Agent.system_type == system_type)
    if agent_code:
        stmt = stmt.where(Agent.agent_code.like(f"%{agent_code}%"))
    if agent_name:
        stmt = stmt.where(Agent.agent_name.like(f"%{agent_name}%"))
    if software_name:
        stmt = stmt.where(Software.name == software_name)
        
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/logs")
async def list_logs(
    db: AsyncSession = Depends(get_db),
    agent_id: Optional[int] = Query(None),
    software_id: Optional[int] = Query(None),
    change_type: Optional[str] = Query(None),
    system_type: Optional[str] = Query(None),
    agent_code: Optional[str] = Query(None),
    agent_name: Optional[str] = Query(None),
    software_name: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    stmt = select(InventoryLog, TransferRecord, InstallationRecord, User).options(
        joinedload(InventoryLog.agent),
        joinedload(InventoryLog.software)
    ).join(InventoryLog.agent).join(InventoryLog.software).outerjoin(
        TransferRecord, InventoryLog.related_id == TransferRecord.id
    ).outerjoin(
        InstallationRecord, InventoryLog.related_id == InstallationRecord.id
    ).outerjoin(User, InventoryLog.operator_id == User.id)
    
    if agent_id:
        stmt = stmt.where(InventoryLog.agent_id == agent_id)
    if software_id:
        stmt = stmt.where(InventoryLog.software_id == software_id)
    if change_type:
        if change_type == 'transfer':
            stmt = stmt.where(InventoryLog.change_type.in_(['transfer_in', 'transfer_out']))
        else:
            stmt = stmt.where(InventoryLog.change_type == change_type)
    if system_type:
        stmt = stmt.where(Agent.system_type == system_type)
    if agent_code:
        stmt = stmt.where(Agent.agent_code.like(f"%{agent_code}%"))
    if agent_name:
        stmt = stmt.where(Agent.agent_name.like(f"%{agent_name}%"))
    if software_name:
        stmt = stmt.where(Software.name == software_name)
    if start_date:
        stmt = stmt.where(InventoryLog.created_at >= start_date)
    if end_date:
        stmt = stmt.where(InventoryLog.created_at <= f"{end_date} 23:59:59")
        
    stmt = stmt.order_by(InventoryLog.created_at.desc())
    result = await db.execute(stmt)
    
    result_list = []
    for log, transfer, install, user in result.all():
        # 获取关联的另一方代理商信息
        to_agent_info = None
        remark = None
        merchant_code = None
        merchant_name = None
        
        if transfer:
            remark = transfer.remark
            if log.change_type == 'transfer_out':
                # 划出记录，关联的是划入方
                to_stmt = select(Agent).where(Agent.id == transfer.to_agent_id)
                to_result = await db.execute(to_stmt)
                to_agent = to_result.scalar_one_or_none()
                if to_agent:
                    to_agent_info = {
                        "system_type": to_agent.system_type,
                        "agent_code": to_agent.agent_code,
                        "agent_name": to_agent.agent_name
                    }
            elif log.change_type == 'transfer_in':
                # 划入记录，关联的是划出方
                from_stmt = select(Agent).where(Agent.id == transfer.from_agent_id)
                from_result = await db.execute(from_stmt)
                from_agent = from_result.scalar_one_or_none()
                if from_agent:
                    to_agent_info = {
                        "system_type": from_agent.system_type,
                        "agent_code": from_agent.agent_code,
                        "agent_name": from_agent.agent_name
                    }
        
        # 获取安装记录的商户信息
        if install:
            merchant_code = install.merchant_code
            merchant_name = install.merchant_name
            remark = install.remark
        
        log_dict = {
            "id": log.id,
            "agent": {
                "id": log.agent.id,
                "agent_code": log.agent.agent_code,
                "agent_name": log.agent.agent_name,
                "system_type": log.agent.system_type
            },
            "software": {
                "id": log.software.id,
                "name": log.software.name
            },
            "change_type": log.change_type,
            "before_qty": log.before_qty,
            "change_qty": log.change_qty,
            "after_qty": log.after_qty,
            "related_id": log.related_id,
            "operator_id": user.username if user else str(log.operator_id),
            "created_at": log.created_at.isoformat() if log.created_at else None,
            "related_system_type": to_agent_info["system_type"] if to_agent_info else None,
            "related_agent_code": to_agent_info["agent_code"] if to_agent_info else None,
            "related_agent_name": to_agent_info["agent_name"] if to_agent_info else None,
            "merchant_code": merchant_code,
            "merchant_name": merchant_name,
            "remark": remark
        }
        result_list.append(log_dict)
    
    return result_list
