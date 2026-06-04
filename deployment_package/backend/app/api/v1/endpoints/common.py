from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.models.database import get_db
from app.models.business import Agent, Software
from app.schemas.business import Agent as AgentSchema, Software as SoftwareSchema
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/agents", response_model=List[AgentSchema])
async def get_agents(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(select(Agent))
    return result.scalars().all()

@router.get("/software", response_model=List[SoftwareSchema])
async def get_software(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(select(Software))
    return result.scalars().all()
