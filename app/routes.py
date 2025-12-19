from fastapi import APIRouter, HTTPException, Depends
from app.schemas import PaymentCreate, PaymentResponse, PaymentStatusUpdate
from app.database import get_db
from app import models
from typing import List
from sqlalchemy.orm import Session

router = APIRouter()

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

@router.patch("/{payment_id}/status", response_model=PaymentResponse)
def update_payment_status(
    payment_id: int,
    update: PaymentStatusUpdate,
    db: Session = Depends(get_db)
):
    payment = db.query(models.Payment).filter(
        models.Payment.id == payment_id
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Optional: validate allowed transitions
    allowed_statuses = {"PENDING", "PAID", "FAILED"}
    if update.payment_status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")

    payment.payment_status = update.payment_status
    db.commit()
    db.refresh(payment)

    # 🔔 OPTIONAL (recommended):
    # notify Order Service if payment succeeded
    if update.payment_status == "PAID":
        notify_order_service(payment.order_id)

    return payment
