from database import Base, engine, get_db
from fastapi import Depends, FastAPI, HTTPException
from models import FlightTable, UserTable
from schemas import FlightCreate, FlightResponse, UserCreate, UserResponse
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Flight Price Comparison API")


@app.get("/")
def read_root():
  return {"message": "Welcome to Flight Price Comparison API!"}


@app.post("/flights/", response_model=FlightResponse)
def create_flight(flight: FlightCreate, db: Session = Depends(get_db)):
  db_flight = FlightTable(**flight.dict())
  db.add(db_flight)
  db.commit()
  db.refresh(db_flight)
  return db_flight


@app.get("/flights/", response_model=list[FlightResponse])
def get_flights(db: Session = Depends(get_db)):
  return db.query(FlightTable).all()


@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
  db_user = db.query(UserTable).filter(UserTable.email == user.email).first()
  if db_user:
    raise HTTPException(status_code=400, detail="Email already registered")
  new_user = UserTable(**user.dict())
  db.add(new_user)
  db.commit()
  db.refresh(new_user)
  return new_user