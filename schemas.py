from pydantic import BaseModel, ConfigDict
from datetime import date

class FlightCreate(BaseModel):
    airline_name: str
    source: str
    destination: str
    price: float
    flight_date: date

class FlightResponse(FlightCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str