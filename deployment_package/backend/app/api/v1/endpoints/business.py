from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.schemas.business import PurchaseCreate, InstallationCreate, TransferCreate
from app.services.inventory_service import InventoryService
from app.api.deps import get_current_user, require_permission
from app.models.user import User

router = APIRouter()

@router.post("/purchase")
async def create_purchase(
    payload: PurchaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("purchase.create"))
):
    try:
        agent = await InventoryService.get_or_create_agent(
            db,
            agent_code=payload.agent_code,
            agent_name=payload.agent_name,
            system_type=payload.system_type
        )
        
        software = await InventoryService.get_or_create_software(
            db,
            name=payload.software_name
        )
        
        purchase = await InventoryService.add_purchase(
            db, 
            agent_id=agent.id,
            software_id=software.id,
            quantity=payload.quantity,
            purchase_date=payload.purchase_date,
            operator_id=current_user.id,
            remark=payload.remark
        )
        await db.commit()
        return {"message": "采购记录已保存", "id": purchase.id}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/install")
async def create_installation(
    payload: InstallationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("installation.create"))
):
    try:
        agent = await InventoryService.get_or_create_agent(
            db,
            agent_code=payload.agent_code,
            agent_name=payload.agent_name,
            system_type=payload.system_type
        )
        
        software = await InventoryService.get_or_create_software(
            db,
            name=payload.software_name
        )
        
        install = await InventoryService.add_installation(
            db,
            agent_id=agent.id,
            software_id=software.id,
            quantity=payload.quantity,
            merchant_code=payload.merchant_code,
            merchant_name=payload.merchant_name,
            install_date=payload.install_date,
            operator_id=current_user.id,
            remark=payload.remark
        )
        await db.commit()
        return {"message": "安装记录已保存", "id": install.id}
    except HTTPException as he:
        await db.rollback()
        raise he
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transfer")
async def create_transfer(
    payload: TransferCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("transfer.create"))
):
    try:
        from_agent = await InventoryService.get_or_create_agent(
            db,
            agent_code=payload.from_agent_code,
            agent_name=payload.from_agent_name,
            system_type=payload.from_system_type
        )
        
        to_agent = await InventoryService.get_or_create_agent(
            db,
            agent_code=payload.to_agent_code,
            agent_name=payload.to_agent_name,
            system_type=payload.to_system_type
        )
        
        software = await InventoryService.get_or_create_software(
            db,
            name=payload.software_name
        )
        
        transfer = await InventoryService.add_transfer(
            db,
            from_agent_id=from_agent.id,
            to_agent_id=to_agent.id,
            software_id=software.id,
            quantity=payload.quantity,
            transfer_date=payload.transfer_date,
            operator_id=current_user.id,
            remark=payload.remark
        )
        await db.commit()
        return {"message": "划拨记录已保存", "id": transfer.id}
    except HTTPException as he:
        await db.rollback()
        raise he
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
