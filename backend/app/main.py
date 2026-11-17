from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.api.routes import r
Base.metadata.create_all(bind=engine)
app=FastAPI(title="OpsPilot AI",version="0.1.0")
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(r)
@app.get("/health")
def health(): return {"status":"ok","service":"opspilot-api"}
@app.get("/health/db")
def health_db():
    with engine.connect() as c: c.exec_driver_sql("SELECT 1")
    return {"status":"ok"}
