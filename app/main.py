from fastapi import FastAPI, Depends
from app.routes import router as payments_router
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db_session as get_db, engine, Base
from prometheus_fastapi_instrumentator import Instrumentator

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Payments Microservice", version="1.0.0")
app.include_router(payments_router, prefix="/payments")

Instrumentator().instrument(app).expose(app)

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except Exception as e:
        return {"status": "error", "db": "error", "detail": str(e)}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Payments Microservice"}