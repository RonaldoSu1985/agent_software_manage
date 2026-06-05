from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, case
from sqlalchemy.orm import joinedload
from typing import List, Optional
from app.models.database import get_db
from app.models.business import Inventory, InventoryLog, Agent, Software, TransferRecord, InstallationRecord
from app.schemas.business import InventoryOut, InventoryLogOut
from app.api.deps import get_current_user
from app.models.user import User
import csv
import io

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

@router.get("/export")
async def export_inventory(
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
    inventories = result.scalars().all()
    
    # 创建CSV文件
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow(['代理商所属系统', '代理商编号', '代理商名称', '软件名称', '库存数量'])
    
    # 写入数据
    for inv in inventories:
        writer.writerow([
            inv.agent.system_type if inv.agent else '',
            inv.agent.agent_code if inv.agent else '',
            inv.agent.agent_name if inv.agent else '',
            inv.software.name if inv.software else '',
            inv.quantity
        ])
    
    # 生成响应
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename=inventory.csv'}
    )

@router.get("/logs/export/purchase")
async def export_purchase_logs(
    db: AsyncSession = Depends(get_db),
    system_type: Optional[str] = Query(None),
    agent_code: Optional[str] = Query(None),
    agent_name: Optional[str] = Query(None),
    software_name: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    operator: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    stmt = select(InventoryLog, User).options(
        joinedload(InventoryLog.agent),
        joinedload(InventoryLog.software)
    ).join(InventoryLog.agent).join(InventoryLog.software).outerjoin(
        User, InventoryLog.operator_id == User.id
    ).where(InventoryLog.change_type == 'purchase')
    
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
    if operator:
        stmt = stmt.where(User.username.like(f"%{operator}%"))
    
    result = await db.execute(stmt)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['代理商所属系统', '代理商编号', '代理商名称', '软件名称', '采购数量', '采购日期', '操作人'])
    
    for log, user in result.all():
        writer.writerow([
            log.agent.system_type if log.agent else '',
            log.agent.agent_code if log.agent else '',
            log.agent.agent_name if log.agent else '',
            log.software.name if log.software else '',
            log.change_qty,
            log.created_at.strftime('%Y-%m-%d') if log.created_at else '',
            user.username if user else str(log.operator_id)
        ])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename=purchase_logs.csv'}
    )

@router.get("/logs/export/installation")
async def export_installation_logs(
    db: AsyncSession = Depends(get_db),
    system_type: Optional[str] = Query(None),
    agent_code: Optional[str] = Query(None),
    agent_name: Optional[str] = Query(None),
    software_name: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    operator: Optional[str] = Query(None),
    merchant_code: Optional[str] = Query(None),
    merchant_name: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    stmt = select(InventoryLog, InstallationRecord, User).options(
        joinedload(InventoryLog.agent),
        joinedload(InventoryLog.software)
    ).join(InventoryLog.agent).join(InventoryLog.software).outerjoin(
        InstallationRecord, InventoryLog.related_id == InstallationRecord.id
    ).outerjoin(User, InventoryLog.operator_id == User.id).where(
        InventoryLog.change_type == 'installation'
    )
    
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
    if operator:
        stmt = stmt.where(User.username.like(f"%{operator}%"))
    if merchant_code:
        stmt = stmt.where(InstallationRecord.merchant_code.like(f"%{merchant_code}%"))
    if merchant_name:
        stmt = stmt.where(InstallationRecord.merchant_name.like(f"%{merchant_name}%"))
    
    result = await db.execute(stmt)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['代理商所属系统', '代理商编号', '代理商名称', '软件名称', '商户编号', '商户名称', '安装数量', '安装日期', '操作人', '备注'])
    
    for log, install, user in result.all():
        writer.writerow([
            log.agent.system_type if log.agent else '',
            log.agent.agent_code if log.agent else '',
            log.agent.agent_name if log.agent else '',
            log.software.name if log.software else '',
            install.merchant_code if install else '',
            install.merchant_name if install else '',
            abs(log.change_qty),
            log.created_at.strftime('%Y-%m-%d') if log.created_at else '',
            user.username if user else str(log.operator_id),
            install.remark if install else ''
        ])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename=installation_logs.csv'}
    )

@router.get("/logs/export/transfer")
async def export_transfer_logs(
    db: AsyncSession = Depends(get_db),
    from_system_type: Optional[str] = Query(None),
    from_agent_code: Optional[str] = Query(None),
    from_agent_name: Optional[str] = Query(None),
    to_system_type: Optional[str] = Query(None),
    to_agent_code: Optional[str] = Query(None),
    to_agent_name: Optional[str] = Query(None),
    software_name: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    operator: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    stmt = select(InventoryLog, TransferRecord, User).options(
        joinedload(InventoryLog.agent),
        joinedload(InventoryLog.software)
    ).join(InventoryLog.agent).join(InventoryLog.software).outerjoin(
        TransferRecord, InventoryLog.related_id == TransferRecord.id
    ).outerjoin(User, InventoryLog.operator_id == User.id).where(
        InventoryLog.change_type == 'transfer_out'
    )
    
    if from_system_type:
        stmt = stmt.where(Agent.system_type == from_system_type)
    if from_agent_code:
        stmt = stmt.where(Agent.agent_code.like(f"%{from_agent_code}%"))
    if from_agent_name:
        stmt = stmt.where(Agent.agent_name.like(f"%{from_agent_name}%"))
    if software_name:
        stmt = stmt.where(Software.name == software_name)
    if start_date:
        stmt = stmt.where(InventoryLog.created_at >= start_date)
    if end_date:
        stmt = stmt.where(InventoryLog.created_at <= f"{end_date} 23:59:59")
    
    result = await db.execute(stmt)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['划出代理商所属系统', '划出代理商编号', '划出代理商名称', '软件名称', '划拨数量', 
                     '划入代理商所属系统', '划入代理商编号', '划入代理商名称', '划拨日期', '备注', '操作人'])
    
    for log, transfer, user in result.all():
        to_agent_info = {}
        if transfer:
            to_stmt = select(Agent).where(Agent.id == transfer.to_agent_id)
            to_result = await db.execute(to_stmt)
            to_agent = to_result.scalar_one_or_none()
            if to_agent:
                to_agent_info = {
                    "system_type": to_agent.system_type,
                    "agent_code": to_agent.agent_code,
                    "agent_name": to_agent.agent_name
                }
        
        writer.writerow([
            log.agent.system_type if log.agent else '',
            log.agent.agent_code if log.agent else '',
            log.agent.agent_name if log.agent else '',
            log.software.name if log.software else '',
            abs(log.change_qty),
            to_agent_info.get("system_type", ''),
            to_agent_info.get("agent_code", ''),
            to_agent_info.get("agent_name", ''),
            log.created_at.strftime('%Y-%m-%d') if log.created_at else '',
            transfer.remark if transfer else '',
            user.username if user else str(log.operator_id)
        ])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename=transfer_logs.csv'}
    )

@router.get("/logs/export/all")
async def export_all_logs(
    db: AsyncSession = Depends(get_db),
    system_type: Optional[str] = Query(None),
    agent_code: Optional[str] = Query(None),
    agent_name: Optional[str] = Query(None),
    software_name: Optional[str] = Query(None),
    change_type: Optional[str] = Query(None),
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
    
    result = await db.execute(stmt)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['代理商所属系统', '代理商编号', '代理商名称', '软件名称', '变动类型', 
                     '变动前库存数量', '变动数量', '变动后库存数量', 
                     '关联操作方所属系统', '关联操作方编号', '关联操作方名称', 
                     '变动时间', '操作人'])
    
    for log, transfer, install, user in result.all():
        to_agent_info = None
        remark = None
        merchant_code_val = None
        merchant_name_val = None
        
        if transfer:
            remark = transfer.remark
            if log.change_type == 'transfer_out':
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
                from_stmt = select(Agent).where(Agent.id == transfer.from_agent_id)
                from_result = await db.execute(from_stmt)
                from_agent = from_result.scalar_one_or_none()
                if from_agent:
                    to_agent_info = {
                        "system_type": from_agent.system_type,
                        "agent_code": from_agent.agent_code,
                        "agent_name": from_agent.agent_name
                    }
        
        if install:
            merchant_code_val = install.merchant_code
            merchant_name_val = install.merchant_name
            remark = install.remark
        
        change_type_label = {
            'purchase': '采购',
            'installation': '商户安装',
            'transfer_in': '划拨(划入)',
            'transfer_out': '划拨(划出)'
        }.get(log.change_type, log.change_type)
        
        related_system_type = ''
        related_agent_code = ''
        related_agent_name = ''
        
        if log.change_type == 'installation':
            related_agent_code = merchant_code_val or ''
            related_agent_name = merchant_name_val or ''
        elif to_agent_info:
            related_system_type = to_agent_info["system_type"] or ''
            related_agent_code = to_agent_info["agent_code"] or ''
            related_agent_name = to_agent_info["agent_name"] or ''
        
        writer.writerow([
            log.agent.system_type if log.agent else '',
            log.agent.agent_code if log.agent else '',
            log.agent.agent_name if log.agent else '',
            log.software.name if log.software else '',
            change_type_label,
            log.before_qty,
            log.change_qty,
            log.after_qty,
            related_system_type,
            related_agent_code,
            related_agent_name,
            log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else '',
            user.username if user else str(log.operator_id)
        ])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename=inventory_logs.csv'}
    )

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
    operator: Optional[str] = Query(None),
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
    if operator:
        stmt = stmt.where(User.username.like(f"%{operator}%"))
        
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
