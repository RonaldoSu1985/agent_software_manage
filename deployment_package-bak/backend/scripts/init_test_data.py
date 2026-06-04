import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.database import Base
from app.models.business import Agent, Software, Inventory
from app.core.config import settings

async def init_test_data():
    """初始化测试数据"""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        # 创建软件数据
        software_list = ['汇客餐饮', '汇客零售']
        
        for name in software_list:
            result = await session.execute(select(Software).filter(Software.name == name))
            software = result.scalar_one_or_none()
            if not software:
                software = Software(name=name)
                session.add(software)
                await session.commit()
                await session.refresh(software)
                print(f"已创建软件: {name}")
            else:
                print(f"软件 {name} 已存在")
        
        # 创建代理商数据
        agent_list = [
            {'agent_code': '000001', 'agent_name': '灿一代理', 'system_type': 'V3系统'},
            {'agent_code': '000101', 'agent_name': '灿二代理', 'system_type': 'V3系统'},
            {'agent_code': 'LTB001', 'agent_name': '阳光早餐店', 'system_type': 'LTB系统'},
        ]
        
        for agent_data in agent_list:
            result = await session.execute(select(Agent).filter(Agent.agent_code == agent_data['agent_code']))
            agent = result.scalar_one_or_none()
            if not agent:
                agent = Agent(**agent_data)
                session.add(agent)
                await session.commit()
                await session.refresh(agent)
                print(f"已创建代理商: {agent_data['agent_name']}")
            else:
                print(f"代理商 {agent_data['agent_name']} 已存在")
        
        # 创建库存数据
        await session.commit()
        
        # 获取所有代理商和软件
        agents_result = await session.execute(select(Agent))
        agents = agents_result.scalars().all()
        
        software_result = await session.execute(select(Software))
        softwares = software_result.scalars().all()
        
        # 为每个代理商创建库存
        for agent in agents:
            for software in softwares:
                result = await session.execute(
                    select(Inventory).filter(Inventory.agent_id == agent.id, Inventory.software_id == software.id)
                )
                inventory = result.scalar_one_or_none()
                if not inventory:
                    # 随机生成初始库存数量
                    import random
                    quantity = random.randint(10, 100)
                    inventory = Inventory(agent_id=agent.id, software_id=software.id, quantity=quantity)
                    session.add(inventory)
                    print(f"已创建库存: {agent.agent_name} - {software.name} - {quantity}")
        
        await session.commit()
        print("测试数据初始化完成")

if __name__ == "__main__":
    asyncio.run(init_test_data())
