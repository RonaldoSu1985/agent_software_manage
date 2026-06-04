from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Date, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    agent_code = Column(String(50), unique=True, nullable=False)
    agent_name = Column(String(100), nullable=False)
    system_type = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=func.now())

    inventories = relationship("Inventory", back_populates="agent")

class Software(Base):
    __tablename__ = "software"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())

    inventories = relationship("Inventory", back_populates="software")

class Inventory(Base):
    __tablename__ = "inventories"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    software_id = Column(Integer, ForeignKey("software.id"), nullable=False)
    quantity = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    agent = relationship("Agent", back_populates="inventories")
    software = relationship("Software", back_populates="inventories")

    __table_args__ = (UniqueConstraint('agent_id', 'software_id', name='uk_agent_software'),)

class PurchaseRecord(Base):
    __tablename__ = "purchase_records"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    software_id = Column(Integer, ForeignKey("software.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    purchase_date = Column(Date, nullable=False)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    remark = Column(Text)
    created_at = Column(DateTime, default=func.now())

class InstallationRecord(Base):
    __tablename__ = "installation_records"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    software_id = Column(Integer, ForeignKey("software.id"), nullable=False)
    merchant_code = Column(String(50), nullable=False)
    merchant_name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    install_date = Column(Date, nullable=False)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    remark = Column(Text)
    created_at = Column(DateTime, default=func.now())

class TransferRecord(Base):
    __tablename__ = "transfer_records"

    id = Column(Integer, primary_key=True, index=True)
    from_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    to_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    software_id = Column(Integer, ForeignKey("software.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    transfer_date = Column(Date, nullable=False)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    remark = Column(Text)
    created_at = Column(DateTime, default=func.now())

class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    software_id = Column(Integer, ForeignKey("software.id"), nullable=False)
    change_type = Column(String(20), nullable=False)
    before_qty = Column(Integer, nullable=False)
    change_qty = Column(Integer, nullable=False)
    after_qty = Column(Integer, nullable=False)
    related_id = Column(Integer)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    agent = relationship("Agent")
    software = relationship("Software")
