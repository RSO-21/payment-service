# 💳 Payment Service

The Payment Service is a microservice responsible for processing and storing payment transactions.  

---

## ✨ Features
- Create and record payments
- Generate unique transaction IDs
- Update payment status
- Auto-generated API documentation

---

## 📚 API Documentation
FastAPI provides interactive documentation:

- **Swagger UI:** http://localhost:8001/docs  

---

## ▶️ Running Locally (without Docker)

### 1. Install dependencies
We suggest you create a virtual environment and activate it. Then install dependencies:
```bash
pip install -r requirements.txt
```
### 2. Start the service
```bash
uvicorn app.main:app --reload --port 8001
```
## 🐳 Running with Docker
### 1. Build the image
docker build -t payment-service:latest .

### 2. Run the container
docker run -p 8001:8000 payment-service:latest
