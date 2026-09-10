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


class UserResponse(UserCreate):
  id: int

  class Config:
    from_attributes = True