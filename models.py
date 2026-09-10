from sqlalchemy import Column, Integer, String, Float, Date
from database import Base

class UserTable(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class FlightTable(Base):
    __tablename__ = "flights"
    id = Column(Integer, primary_key=True, index=True)
    airline_name = Column(String, index=True)
    source = Column(String, index=True)
    destination = Column(String, index=True)
    price = Column(Float)
    flight_date = Column(Date)