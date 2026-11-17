import os
os.environ["DATABASE_URL"]="sqlite:///./test.db"
from fastapi.testclient import TestClient
from app.main import app
def test_health(): assert TestClient(app).get("/health").status_code==200
