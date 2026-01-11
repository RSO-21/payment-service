# app/models.py
from sqlalchemy import Column, Integer, DateTime, String, Numeric, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, nullable=False)
    user_id = Column(String(36), nullable=False)

    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), nullable=False, default="EUR")

    payment_method = Column(String(50), nullable=False)
    payment_status = Column(String(20), nullable=False, default="pending")
    provider = Column(String(50), nullable=False)
    transaction_id = Column(
        String(255),
        nullable=False,
        default=lambda: str(uuid.uuid4()),
        unique=True,
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class PaymentLookup(Base):
    __tablename__ = "payment_lookup"
    __table_args__ = {"schema": "public"}

    external_id = Column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False
    )

    payment_id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(100), nullable=False)
    order_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
