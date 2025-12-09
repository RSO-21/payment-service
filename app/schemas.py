from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import List
from decimal import Decimal

## Order schemas
class PaymentCreate(BaseModel):
    order_id: int
    user_id: int
    amount: Decimal
    currency: str
    payment_method: str
    provider: str

class PaymentResponse(BaseModel):
    id: int
    order_id: int
    user_id: int
    amount: Decimal
    currency: str
    payment_method: str
    payment_status: str
    provider: str
    transaction_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

