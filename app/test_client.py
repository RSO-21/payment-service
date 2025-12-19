import grpc
import app.payment_pb2
import app.payment_pb2_grpc

def run():
    channel = grpc.insecure_channel('127.0.0.1:50051')
    stub = app.payment_pb2_grpc.PaymentServiceStub(channel)

    # Example payment request
    request = app.payment_pb2.PaymentRequest(user_id="user123", amount=500)
    response = stub.PaymentCreate(request)

    print(f"Payment status: {response.status}, message: {response.message}")

if __name__ == "__main__":
    run()
