import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.database import get_db_session as get_db
from app.rabbitmq_publisher import publish_payment_confirmed
from app.schemas import PaymentCreate, PaymentResponse, PaymentStatusUpdate

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[PaymentResponse])
def list_payments(db: Session = Depends(get_db)):
    return db.query(models.Payment).all()


@router.post("/", response_model=PaymentResponse, status_code=201)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    # create payment instance
    db_payment = models.Payment(**payment.dict())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Order not found")

    return payment

def notify_order_service(order_id: int):
    # TODO: replace with real HTTP/gRPC call later
    print(f"[PAYMENT] Order {order_id} marked as PAID")

@router.post("/{payment_id}/confirm", response_model=PaymentResponse)
def confirm_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment.payment_status = "PAID"
    db.commit()
    db.refresh(payment)

    try:
        publish_payment_confirmed(payment.id, payment.order_id, payment.payment_status)
    except Exception as exc:
        logger.error("Failed to publish payment_confirmed event: %s", exc, exc_info=True)
    
    return payment
