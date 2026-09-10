from database import Base
from sqlalchemy import Column, Float, Integer, String


class FlightTable(Base):
  __tablename__ = "flights"

  id = Column(Integer, primary_key=True, index=True)
  airline_name = Column(String, index=True)
  source = Column(String, index=True)
  destination = Column(String, index=True)
  price = Column(Float)
  flight_date = Column(String)


class UserTable(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key=True, index=True)
  username = Column(String, unique=True, index=True)
  email = Column(String, unique=True, index=True)