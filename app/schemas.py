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
    min_price: float
    max_price: float


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
    min_price: float
    max_price: float


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

    payments_water: float
    payments_wastewater: float
    payments_rainwater: float

    fixed_price: float

    note: Optional[str] = None


class WaterCreate(Water):
    pass


class WaterResponse(Water):
    id: int

    price_water: float
    price_wastewater: float
    price_rainwater: float

    monthly_payment_water: float
    monthly_payment_wastewater: float
    monthly_payment_rainwater: float

    difference_water: float
    difference_wastewater: float
    difference_rainwater: float

    class Config:
        from_attributes = True


class WaterOverallStats(BaseModel):
    total_volume_water: float
    total_volume_wastewater: float
    total_volume_rainwater: float

    total_costs_water: float
    total_costs_wastewater: float
    total_costs_rainwater: float

    total_payments_water: float
    total_payments_wastewater: float
    total_payments_rainwater: float

    total_difference_water: float
    total_difference_wastewater: float
    total_difference_rainwater: float

    total_fixed_price: float

    number_of_years: int

    average_yearly_volume_water: float
    average_yearly_volume_wastewater: float
    average_yearly_volume_rainwater: float

    average_yearly_costs_water: float
    average_yearly_costs_wastewater: float
    average_yearly_costs_rainwater: float

    average_yearly_fixed_price: float

    total_costs: float
    average_usage: float


class WaterPriceTrend(BaseModel):
    year: int
    average_price_water: float
    average_price_wastewater: float
    average_price_rainwater: float

    min_price_water: float
    min_price_wastewater: float
    min_price_rainwater: float

    max_price_water: float
    max_price_wastewater: float
    max_price_rainwater: float

    average_fixed_price: float
    min_fixed_price: float
    max_fixed_price: float


class WaterYearlySummary(BaseModel):
    year: int

    total_volume_water: float
    total_volume_wastewater: float
    total_volume_rainwater: float

    total_costs_water: float
    total_costs_wastewater: float
    total_costs_rainwater: float

    total_payments_water: float
    total_payments_wastewater: float
    total_payments_rainwater: float

    volume_wastewater: int
    costs_wastewater: float
