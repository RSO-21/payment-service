FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir grpcio-tools
COPY . .
RUN python -m grpc_tools.protoc \
  -I/app/protos \
  --python_out=/app/app/grpc \
  --grpc_python_out=/app/app/grpc \
  /app/protos/payment.proto
RUN sed -i 's/^import payment_pb2 as payment__pb2$/from . import payment_pb2 as payment__pb2/' /app/app/grpc/payment_pb2_grpc.py
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
