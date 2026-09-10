from pydantic import BaseModel


class FlightCreate(BaseModel):
  airline_name: str
  source: str
  destination: str
  price: float
  flight_date: str


class FlightResponse(FlightCreate):
  id: int

  class Config:
    from_attributes = True


class UserCreate(BaseModel):
  username: str
  email: str
  password: str  # Signup ke waqt password ke liye


class UserResponse(BaseModel):
  id: int
  username: str
  email: str  # Response mein password nahi dikhega (security ke liye)

  class Config:
    from_attributes = True


class Token(BaseModel):
  access_token: str
  token_type: str


class TokenData(BaseModel):
  email: str | None = None