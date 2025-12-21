# payment_service/server.py
import grpc
from concurrent import futures
from app import models, database
from app.grpc import payment_pb2_grpc, payment_pb2
from sqlalchemy.orm import Session
from app.rabbitmq_publisher import publish_payment_confirmed

class PaymentServicer(payment_pb2_grpc.PaymentServiceServicer):

    def CreatePayment(self, request, context):
        db = database.get_db_session()

        payment = models.Payment(
            order_id=request.order_id,
            user_id=request.user_id,
            amount=request.amount,
            currency=request.currency or "EUR",
            payment_method=request.payment_method,
            provider=request.provider,
            payment_status="PENDING"
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        return payment_pb2.PaymentResponse(
            payment_id=payment.id,
            order_id=payment.order_id,
            status=payment.payment_status
        )

    def ConfirmPayment(self, request, context):
        db = database.get_db_session()
        payment = db.query(models.Payment).filter(models.Payment.id == request.payment_id).first()
        if not payment:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Payment not found")
            return payment_pb2.PaymentResponse()
        payment.payment_status = request.status
        db.commit()
        db.refresh(payment)

        publish_payment_confirmed(payment.id, payment.order_id, payment.payment_status)

        return payment_pb2.PaymentResponse(payment_id=payment.id, order_id=payment.order_id, status=payment.payment_status)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    payment_pb2_grpc.add_PaymentServiceServicer_to_server(PaymentServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
