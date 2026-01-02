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
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
