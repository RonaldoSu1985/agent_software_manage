from mcp.server.fastmcp import FastMCP
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.models.database import AsyncSessionLocal
from app.models.business import Agent, Software, Inventory, InventoryLog
from app.models.user import User
from app.services.inventory_service import InventoryService
from datetime import date
import logging
import contextvars

logger = logging.getLogger(__name__)

# 用于存储当前操作的用户ID
current_user_id = contextvars.ContextVar("current_user_id", default=None)

mcp = FastMCP("软件管理系统 MCP 服务")

@mcp.tool()
async def list_inventory(system_type: str = None, agent_code: str = None, software_name: str = None):
    """
    列出库存信息。
    :param system_type: 系统类型过滤（可选）
    :param agent_code: 代理商编号过滤（可选）
    :param software_name: 软件名称过滤（可选）
    """
    async with AsyncSessionLocal() as db:
        stmt = select(Inventory).options(
            joinedload(Inventory.agent),
            joinedload(Inventory.software)
        ).join(Agent).join(Software)
        
        if system_type:
            stmt = stmt.where(Agent.system_type == system_type)
        if agent_code:
            stmt = stmt.where(Agent.agent_code == agent_code)
        if software_name:
            stmt = stmt.where(Software.name == software_name)
            
        result = await db.execute(stmt)
        inventories = result.scalars().all()
        
        return [
            {
                "system_type": inv.agent.system_type,
                "agent_code": inv.agent.agent_code,
                "agent_name": inv.agent.agent_name,
                "software_name": inv.software.name,
                "quantity": inv.quantity
            }
            for inv in inventories
        ]

@mcp.tool()
async def record_purchase(agent_code: str, agent_name: str, system_type: str, software_name: str, quantity: int, remark: str = None):
    """
    记录一笔采购记录。
    :param agent_code: 代理商编号
    :param agent_name: 代理商名称
    :param system_type: 系统类型
    :param software_name: 软件名称
    :param quantity: 采购数量
    :param remark: 备注（可选）
    """
    user_id = current_user_id.get()
    if not user_id:
        return "错误：未识别的用户上下文"

    async with AsyncSessionLocal() as db:
        async with db.begin():
            agent = await InventoryService.get_or_create_agent(db, agent_code, agent_name, system_type)
            software = await InventoryService.get_or_create_software(db, software_name)
            
            await InventoryService.add_purchase(
                db, 
                agent_id=agent.id, 
                software_id=software.id, 
                quantity=quantity, 
                purchase_date=date.today(), 
                operator_id=user_id, 
                remark=remark
            )
        return f"成功：已为 {agent_name} ({agent_code}) 记录 {quantity} 套 {software_name} 的采购记录。"

@mcp.tool()
async def record_installation(agent_code: str, system_type: str, software_name: str, quantity: int, merchant_code: str, merchant_name: str, remark: str = None):
    """
    记录一笔商户安装记录。
    :param agent_code: 代理商编号
    :param system_type: 系统类型
    :param software_name: 软件名称
    :param quantity: 安装数量
    :param merchant_code: 商户编号
    :param merchant_name: 商户名称
    :param remark: 备注（可选）
    """
    user_id = current_user_id.get()
    if not user_id:
        return "错误：未识别的用户上下文"

    async with AsyncSessionLocal() as db:
        async with db.begin():
            stmt = select(Agent).where(Agent.agent_code == agent_code, Agent.system_type == system_type)
            result = await db.execute(stmt)
            agent = result.scalar_one_or_none()
            if not agent:
                return f"错误：找不到代理商 {agent_code} ({system_type})"
                
            software = await InventoryService.get_or_create_software(db, software_name)
            
            try:
                await InventoryService.add_installation(
                    db,
                    agent_id=agent.id,
                    software_id=software.id,
                    quantity=quantity,
                    merchant_code=merchant_code,
                    merchant_name=merchant_name,
                    install_date=date.today(),
                    operator_id=user_id,
                    remark=remark
                )
            except Exception as e:
                return f"错误：{str(e)}"
                
        return f"成功：已记录商户 {merchant_name} 的 {software_name} 安装记录。"

@mcp.tool()
async def record_transfer(from_agent_code: str, from_system_type: str, to_agent_code: str, to_system_type: str, software_name: str, quantity: int, remark: str = None):
    """
    记录一笔代理商之间的划拨记录。
    """
    user_id = current_user_id.get()
    if not user_id:
        return "错误：未识别的用户上下文"

    async with AsyncSessionLocal() as db:
        async with db.begin():
            from_stmt = select(Agent).where(Agent.agent_code == from_agent_code, Agent.system_type == from_system_type)
            from_result = await db.execute(from_stmt)
            from_agent = from_result.scalar_one_or_none()
            
            to_stmt = select(Agent).where(Agent.agent_code == to_agent_code, Agent.system_type == to_system_type)
            to_result = await db.execute(to_stmt)
            to_agent = to_result.scalar_one_or_none()
            
            if not from_agent or not to_agent:
                return "错误：找不到划出方或划入方代理商"
                
            software = await InventoryService.get_or_create_software(db, software_name)
            
            try:
                await InventoryService.add_transfer(
                    db,
                    from_agent_id=from_agent.id,
                    to_agent_id=to_agent.id,
                    software_id=software.id,
                    quantity=quantity,
                    transfer_date=date.today(),
                    operator_id=user_id,
                    remark=remark
                )
            except Exception as e:
                return f"错误：{str(e)}"
                
        return f"成功：已完成从 {from_agent.agent_name} 到 {to_agent.agent_name} 的 {software_name} 划拨。"
