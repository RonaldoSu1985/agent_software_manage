from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.business import Agent, Software, Inventory, InventoryLog, PurchaseRecord, InstallationRecord, TransferRecord
from fastapi import HTTPException
from datetime import date

class InventoryService:
    @staticmethod
    async def get_or_create_agent(db: AsyncSession, agent_code: str, agent_name: str, system_type: str):
        stmt = select(Agent).where(Agent.agent_code == agent_code, Agent.system_type == system_type)
        result = await db.execute(stmt)
        agent = result.scalar_one_or_none()
        if not agent:
            agent = Agent(agent_code=agent_code, agent_name=agent_name, system_type=system_type)
            db.add(agent)
            await db.flush()
        return agent

    @staticmethod
    async def get_or_create_software(db: AsyncSession, name: str):
        stmt = select(Software).where(Software.name == name)
        result = await db.execute(stmt)
        software = result.scalar_one_or_none()
        if not software:
            software = Software(name=name)
            db.add(software)
            await db.flush()
        return software

    @staticmethod
    async def get_or_create_inventory(db: AsyncSession, agent_id: int, software_id: int):
        stmt = select(Inventory).where(Inventory.agent_id == agent_id, Inventory.software_id == software_id)
        result = await db.execute(stmt)
        inventory = result.scalar_one_or_none()
        if not inventory:
            inventory = Inventory(agent_id=agent_id, software_id=software_id, quantity=0)
            db.add(inventory)
            await db.flush()
        return inventory

    @staticmethod
    async def add_purchase(db: AsyncSession, agent_id: int, software_id: int, quantity: int, purchase_date: date, operator_id: int, remark: str = None):
        inventory = await InventoryService.get_or_create_inventory(db, agent_id, software_id)
        
        before_qty = inventory.quantity
        inventory.quantity += quantity
        after_qty = inventory.quantity
        
        purchase = PurchaseRecord(
            agent_id=agent_id,
            software_id=software_id,
            quantity=quantity,
            purchase_date=purchase_date,
            operator_id=operator_id,
            remark=remark
        )
        db.add(purchase)
        await db.flush()

        log = InventoryLog(
            agent_id=agent_id,
            software_id=software_id,
            change_type="purchase",
            before_qty=before_qty,
            change_qty=quantity,
            after_qty=after_qty,
            related_id=purchase.id,
            operator_id=operator_id
        )
        db.add(log)
        return purchase

    @staticmethod
    async def add_installation(db: AsyncSession, agent_id: int, software_id: int, quantity: int, merchant_code: str, merchant_name: str, install_date: date, operator_id: int, remark: str = None):
        inventory = await InventoryService.get_or_create_inventory(db, agent_id, software_id)
        
        if inventory.quantity < quantity:
            raise HTTPException(status_code=400, detail="库存不足")
        
        before_qty = inventory.quantity
        inventory.quantity -= quantity
        after_qty = inventory.quantity
        
        install = InstallationRecord(
            agent_id=agent_id,
            software_id=software_id,
            merchant_code=merchant_code,
            merchant_name=merchant_name,
            quantity=quantity,
            install_date=install_date,
            operator_id=operator_id,
            remark=remark
        )
        db.add(install)
        await db.flush()

        log = InventoryLog(
            agent_id=agent_id,
            software_id=software_id,
            change_type="installation",
            before_qty=before_qty,
            change_qty=-quantity,
            after_qty=after_qty,
            related_id=install.id,
            operator_id=operator_id
        )
        db.add(log)
        return install

    @staticmethod
    async def add_transfer(db: AsyncSession, from_agent_id: int, to_agent_id: int, software_id: int, quantity: int, transfer_date: date, operator_id: int, remark: str = None):
        if from_agent_id == to_agent_id:
            raise HTTPException(status_code=400, detail="不能在相同代理商之间划拨")
            
        from_inv = await InventoryService.get_or_create_inventory(db, from_agent_id, software_id)
        to_inv = await InventoryService.get_or_create_inventory(db, to_agent_id, software_id)
        
        if from_inv.quantity < quantity:
            raise HTTPException(status_code=400, detail="划出方库存不足")
            
        # From agent
        before_qty_from = from_inv.quantity
        from_inv.quantity -= quantity
        after_qty_from = from_inv.quantity
        
        # To agent
        before_qty_to = to_inv.quantity
        to_inv.quantity += quantity
        after_qty_to = to_inv.quantity
        
        transfer = TransferRecord(
            from_agent_id=from_agent_id,
            to_agent_id=to_agent_id,
            software_id=software_id,
            quantity=quantity,
            transfer_date=transfer_date,
            operator_id=operator_id,
            remark=remark
        )
        db.add(transfer)
        await db.flush()
        
        # Log for from agent
        log_from = InventoryLog(
            agent_id=from_agent_id,
            software_id=software_id,
            change_type="transfer_out",
            before_qty=before_qty_from,
            change_qty=-quantity,
            after_qty=after_qty_from,
            related_id=transfer.id,
            operator_id=operator_id
        )
        db.add(log_from)
        
        # Log for to agent
        log_to = InventoryLog(
            agent_id=to_agent_id,
            software_id=software_id,
            change_type="transfer_in",
            before_qty=before_qty_to,
            change_qty=quantity,
            after_qty=after_qty_to,
            related_id=transfer.id,
            operator_id=operator_id
        )
        db.add(log_to)
        
        return transfer
