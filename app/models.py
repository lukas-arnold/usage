from sqlalchemy import Column, Integer, Float, String, Date
from .database import Base


class ElectricityDB(Base):
    __tablename__ = "electricity"

    id = Column(Integer, primary_key=True, index=True)
    time_from = Column(Date, nullable=False)
    time_to = Column(Date, nullable=False)
    usage = Column(Integer, nullable=False)
    costs = Column(Float, nullable=False)
    retailer = Column(String, nullable=False)
    payments = Column(Float, nullable=False)
    note = Column(String, nullable=True)


class OilDB(Base):
    __tablename__ = "oil"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    volume = Column(Integer, nullable=False)
    costs = Column(Float, nullable=False)
    retailer = Column(String, nullable=False)
    note = Column(String, nullable=True)


class WaterDB(Base):
    __tablename__ = "water"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    volume_consumed_water = Column(Integer, nullable=False)
    costs_water = Column(Float, nullable=False)
    costs_wastewater = Column(Float, nullable=False)
    volume_rainwater = Column(Integer, nullable=False)
    costs_rainwater = Column(Float, nullable=False)
    payments_water = Column(Float, nullable=False)
    payments_wastewater = Column(Float, nullable=False)
    note = Column(String, nullable=True)
