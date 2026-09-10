from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from database import Base, get_db
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_sql_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def setup_function():
    Base.metadata.create_all(bind=engine)

def teardown_function():
    engine.dispose()
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_sql_app.db"):
        try:
            os.remove("./test_sql_app.db")
        except PermissionError:
            pass

def test_flow():
    user_payload = {"username": "admin", "email": "admin@test.com", "password": "password123"}
    res = client.post("/users/", json=user_payload)
    assert res.status_code in [200, 201]

    login_res = client.post("/token", data={"username": "admin", "password": "password123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    flight_data = {
        "airline_name": "Indigo",
        "source": "Delhi",
        "destination": "Mumbai",
        "price": 5500.0,
        "flight_date": "2026-06-15"
    }
    flight_res = client.post("/flights/", json=flight_data, headers={"Authorization": f"Bearer {token}"})
    assert flight_res.status_code in [200, 201]
    assert flight_res.json()["airline_name"] == "Indigo"