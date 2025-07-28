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
        from_attributes = True


class ElectricityOverallStats(BaseModel):
    total_usage: float
    total_costs: float
    number_of_years: int
    average_yearly_usage: float


class ElectricityPriceTrend(BaseModel):
    year: int
    average_price: float


class ElectricityYearlySummary(BaseModel):
    year: int
    total_usage: float
    total_costs: float


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

    class Config:
        from_attributes = True


class OilOverallStats(BaseModel):
    total_volume: float
    total_costs: float
    number_of_years: int
    average_yearly_volume: float


class OilPriceTrend(BaseModel):
    year: int
    average_price: float


class OilYearlySummary(BaseModel):
    year: int
    total_volume: float
    total_costs: float


class Water(BaseModel):
    year: int
    volume_water: int
    volume_wastewater: int
    volume_rainwater: int
    costs_water: float
    costs_wastewater: float
    costs_rainwater: float
    payments: float
    fixed_price: float
    note: Optional[str] = None


class WaterCreate(Water):
    pass


class WaterResponse(Water):
    id: int
    price_water: float
    price_wastewater: float
    price_rainwater: float
    monthly_payment: float
    difference: float

    class Config:
        from_attributes = True


class WaterOverallStats(BaseModel):
    total_volume: int
    total_costs: float
    number_of_years: int
    average_volume: float


class WaterYearlySummary(BaseModel):
    year: int
    volume_water: int
    volume_wastewater: int
    costs_water: float
    costs_wastewater: float


class WaterPriceTrend(BaseModel):
    year: int
    price_water: float
    price_wastewater: float
    price_rainwater: float
    price_fixed: float
