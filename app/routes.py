import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app import models
from app.database import get_db_session as get_db
from app.rabbitmq_publisher import publish_payment_confirmed
from app.schemas import PaymentCreate, PaymentResponse, PaymentStatusUpdate
from sqlalchemy import text

router = APIRouter()
logger = logging.getLogger(__name__)

def get_tenant_id(x_tenant_id: Optional[str] = Header(None)) -> str:
    """Extract tenant ID from header, default to public"""
    return x_tenant_id or "public"

def get_db_with_schema(tenant_id: str = Depends(get_tenant_id)):
    with get_db(schema=tenant_id) as db:
        yield db

@router.get("/", response_model=List[PaymentResponse])
def list_payments(db: Session = Depends(get_db_with_schema)):
    return db.query(models.Payment).all()


@router.post("/", response_model=PaymentResponse, status_code=201)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db_with_schema), tenant_id: str = Depends(get_tenant_id)):
    db_payment = models.Payment(**payment.dict())
    db.add(db_payment)
    db.flush()


    sql = text("""
        INSERT INTO public.payment_lookup (payment_id, tenant_id, order_id) 
        VALUES (:pid, :tid, :oid)
    """)
    
    result = db.execute(sql, {
        "pid": db_payment.transaction_id, 
        "tid": tenant_id, 
        "oid": db_payment.order_id
    })

    external_id = result.scalar()

    db.commit()
    db.refresh(db_payment)
    
    return {
        **db_payment.__dict__, 
        "external_id": external_id
    }

@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db_with_schema)):
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Order not found")

    return payment

def notify_order_service(order_id: int):
    # TODO: replace with real HTTP/gRPC call later
    print(f"[PAYMENT] Order {order_id} marked as PAID")

@router.post("/orders/{order_id}/confirm", response_model=PaymentResponse)
def confirm_payment_for_order(
    order_id: int,
    external_id: str, db: Session = Depends(get_db_with_schema),
    tenant_id: str = Depends(get_tenant_id),
):
    lookup = db.query(models.PaymentLookup).filter(
        models.PaymentLookup.external_id == external_id
    ).first()

    if not lookup:
        raise HTTPException(status_code=404, detail="Payment reference not found")

    # 2. Nastavi shemo na podlagi najdenega tenanta
    tenant_id = lookup.tenant_id
    db.execute(text(f"SET search_path TO {tenant_id}"))

    payment = db.query(models.Payment).filter(
        models.Payment.order_id == order_id
    ).first()

    if not payment:
        raise HTTPException(404, "Payment not found")

    payment.payment_status = "PAID"
    db.commit()
    db.refresh(payment)

    publish_payment_confirmed(
        payment.id,
        payment.order_id,
        payment.payment_status,
        user_id=str(payment.user_id),
        amount=float(payment.amount),
        tenant_id=tenant_id
    )

    return payment

