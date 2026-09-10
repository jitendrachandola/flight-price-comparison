from database import engine, get_db
from fastapi import Depends, FastAPI, HTTPException
import models
import schemas
from sqlalchemy.orm import Session

# Yeh database ke andar tables bana dega agar pehle se nahi bani hain
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Flight Price Comparison API")


# Feature 1: New flight ka data db mein save karna
@app.post("/flights/", response_model=schemas.FlightResponse)
def add_flight(flight: schemas.FlightCreate, db: Session = Depends(get_db)):
  db_flight = models.FlightTable(
      airline_name=flight.airline_name,
      source=flight.source,
      destination=flight.destination,
      price=flight.price,
  )
  db.add(db_flight)
  db.commit()
  db.refresh(db_flight)
  return db_flight


# Feature 2: Saari saved flights ki list dekhna
@app.get("/flights/", response_model=list[schemas.FlightResponse])
def get_flights(db: Session = Depends(get_db)):
  return db.query(models.FlightTable).all()

#Feature 3: New user db mai save krna
@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
  db_user = models.UserTable(username=user.username, email=user.email)
  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return db_user


# Naya Feature: Saare Registered Users Ki List Dekhna
@app.get("/users/", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
  return db.query(models.UserTable).all()