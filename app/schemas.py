from pydantic import BaseModel
from datetime import date
from typing import Optional


class Electricity(BaseModel):
    time_from: date
    time_to: date
    usage: int
    costs: float
    retailer: str
    payments: float
    note: Optional[str] = None


class ElectricityCreate(Electricity):
    pass


class ElectricityResponse(Electricity):
    id: int
    price: float
    monthly_payment: float
    difference: float

    class Config:
        orm_mode = True


class ElectricityOverallStats(BaseModel):
    total_usage: float
    total_costs: float
    number_of_years: int
    average_yearly_usage: float


class ElectricityPriceTrend(BaseModel):
    year: int
    average_price: float
    min_price: float
    max_price: float


class Oil(BaseModel):
    date: date
    volume: int
    costs: float
    retailer: str
    note: Optional[str] = None


class OilCreate(Oil):
    pass


class OilResponse(Oil):
    id: int
    price: float
    year_usage: float
    year_costs: float
    year: int

    class Config:
        orm_mode = True


class OilOverallStats(BaseModel):
    total_volume: float
    total_costs: float
    number_of_years: int
    average_yearly_volume: float


class OilPriceTrend(BaseModel):
    year: int
    average_price: float
    min_price: float
    max_price: float


class Water(BaseModel):
    year: int
    volume_consumed_water: int
    costs_water: float
    costs_wastewater: float
    volume_rainwater: int
    costs_rainwater: float
    note: Optional[str] = None


class WaterCreate(Water):
    pass


class WaterResponse(BaseModel):
    id: int
    year: int
    volume_consumed_water: int
    costs_water: float
    costs_wastewater: float
    volume_rainwater: int
    costs_rainwater: float
    note: Optional[str] = None

    price_water: float
    price_wastewater: float
    price_rainwater: float
    total_costs: float

    class Config:
        orm_mode = True


class WaterOverallStats(BaseModel):
    total_volume_consumed_water: float
    total_volume_rainwater: float
    total_costs_water: float
    total_costs_wastewater: float
    total_costs_rainwater: float
    number_of_years: int
    average_yearly_volume_consumed_water: float
    average_yearly_volume_rainwater: float
    average_yearly_costs_water: float
    average_yearly_costs_wastewater: float
    average_yearly_costs_rainwater: float


class WaterPriceTrend(BaseModel):
    year: int
    average_price_water: float
    average_price_wastewater: float
    average_price_rainwater: float
    min_price_water: float
    max_price_water: float
    min_price_wastewater: float
    max_price_wastewater: float
    min_price_rainwater: float
    max_price_rainwater: float
