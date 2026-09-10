from datetime import datetime, timedelta
from database import Base, engine, get_db
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from models import FlightTable, UserTable
from passlib.context import CryptContext
from schemas import (
    FlightCreate,
    FlightResponse,
    Token,
    UserCreate,
    UserResponse,
)
from sqlalchemy.orm import Session

# Security Configurations
SECRET_KEY = "supersecretkeychangeinproduction"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Flight Price Comparison API")


# Helper Functions for Security
def verify_password(plain_password, hashed_password):
  return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
  return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
  to_encode = data.copy()
  expire = datetime.utcnow() + (
      expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  )
  to_encode.update({"exp": expire})
  return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
  credentials_exception = HTTPException(
      status_code=401,
      detail="Could not validate credentials",
      headers={"WWW-Authenticate": "Bearer"},
  )
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email: str = payload.get("sub")
    if email is None:
      raise credentials_exception
  except JWTError:
    raise credentials_exception
  user = db.query(UserTable).filter(UserTable.email == email).first()
  if user is None:
    raise credentials_exception
  return user


# Root Endpoint
@app.get("/")
def read_root():
  return {"message": "Welcome to Flight Price Comparison API!"}


# User Signup Endpoint
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
  db_user = db.query(UserTable).filter(UserTable.email == user.email).first()
  if db_user:
    raise HTTPException(status_code=400, detail="Email already registered")

  hashed_pwd = get_password_hash(user.password)
  new_user = UserTable(
      username=user.username, email=user.email, hashed_password=hashed_pwd
  )
  db.add(new_user)
  db.commit()
  db.refresh(new_user)
  return new_user


# Login Endpoint (Get Token)
@app.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
  user = (
      db.query(UserTable)
      .filter(UserTable.email == form_data.username)
      .first()
  )
  if not user or not verify_password(form_data.password, user.hashed_password):
    raise HTTPException(
        status_code=401,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
  access_token = create_access_token(data={"sub": user.email})
  return {"access_token": access_token, "token_type": "bearer"}


# Get Current Logged-in User Profile
@app.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: UserTable = Depends(get_current_user)):
  return current_user


# Protected Flight Creation Endpoint
@app.post("/flights/", response_model=FlightResponse)
def create_flight(
    flight: FlightCreate,
    db: Session = Depends(get_db),
    current_user: UserTable = Depends(get_current_user),
):
  db_flight = FlightTable(**flight.dict())
  db.add(db_flight)
  db.commit()
  db.refresh(db_flight)
  return db_flight


# Get All Flights with Optional Source/Destination Filters
@app.get("/flights/", response_model=list[FlightResponse])
def get_flights(
    source: str | None = None,
    destination: str | None = None,
    db: Session = Depends(get_db),
):
  query = db.query(FlightTable)
  if source:
    query = query.filter(FlightTable.source == source)
  if destination:
    query = query.filter(FlightTable.destination == destination)
  return query.all()