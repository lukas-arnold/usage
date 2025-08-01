from pydantic import BaseModel, Field
from datetime import date as date_
from typing import Optional

# --- Electricity Schemas ---
# This section defines the data models for electricity consumption and billing.


class ElectricityBase(BaseModel):
    """
    Base schema for an electricity bill or reading.
    This class defines the core attributes common to all electricity records.
    """

    time_from: date_ = Field(..., description="Start date of the billing period.")
    time_to: date_ = Field(..., description="End date of the billing period.")
    usage: int = Field(
        ..., description="Total electricity usage in kWh for the period."
    )
    costs: float = Field(
        ...,
        description="Total costs of electricity for the period, excluding payments made.",
    )
    retailer: str = Field(..., description="Name of the electricity retailer.")
    payments: float = Field(
        ..., description="Total amount paid to the retailer during the period."
    )
    note: Optional[str] = Field(
        None, description="Optional notes about the electricity record."
    )


class ElectricityCreate(ElectricityBase):
    """
    Schema for creating a new electricity record.
    It inherits all fields from `ElectricityBase`.
    """

    pass


class ElectricityResponse(ElectricityBase):
    """
    Schema for an electricity record retrieved from the database.
    It extends `ElectricityBase` with additional calculated or database-specific fields.
    """

    id: int = Field(..., description="Unique identifier for the electricity record.")
    price: float = Field(..., description="Calculated price per kWh for the period.")
    monthly_payment: float = Field(
        ...,
        description="Calculated average monthly payment based on the billing period.",
    )
    difference: float = Field(
        ...,
        description="Difference between total costs and total payments for the period.",
    )

    class Config:
        """
        Pydantic configuration class.
        `from_attributes = True` allows the model to be created from ORM objects.
        """

        from_attributes = True


class ElectricityOverallStats(BaseModel):
    """
    Schema for overall electricity consumption statistics.
    """

    total_usage: float = Field(
        ..., description="Total electricity usage across all records in kWh."
    )
    total_costs: float = Field(
        ..., description="Total electricity costs across all records."
    )
    number_of_years: float = Field(
        ..., description="Total number of years covered by the data."
    )
    average_usage: float = Field(
        ..., description="Average annual electricity usage in kWh."
    )


class ElectricityPriceTrend(BaseModel):
    """
    Schema for representing the electricity price trend on a yearly basis.
    """

    year: int = Field(..., description="Year of the data point.")
    average_price: float = Field(
        ..., description="Average price per kWh for the given year."
    )


class ElectricityYearlySummary(BaseModel):
    """
    Schema for a summary of electricity data for a single year.
    """

    year: int = Field(..., description="Year of the summary.")
    total_usage: float = Field(
        ..., description="Total electricity usage for the year in kWh."
    )
    total_costs: float = Field(..., description="Total electricity costs for the year.")


# --- Oil Schemas ---
# This section defines the data models for oil consumption and fill levels.


class OilBase(BaseModel):
    """
    Base schema for an oil delivery record.
    """

    date: date_ = Field(..., description="Date of the oil delivery.")
    volume: int = Field(..., description="Volume of the oil delivery in liters.")
    costs: float = Field(..., description="Total costs of the oil delivery.")
    retailer: str = Field(..., description="Name of the oil retailer.")
    note: Optional[str] = Field(
        None, description="Optional notes about the oil delivery."
    )


class OilCreate(OilBase):
    """
    Schema for creating a new oil delivery record.
    """

    pass


class OilResponse(OilBase):
    """
    Schema for an oil delivery record retrieved from the database.
    """

    id: int = Field(..., description="Unique identifier for the oil record.")
    price: float = Field(..., description="Calculated price per liter of oil.")
    year_usage: float = Field(
        ..., description="Calculated oil usage for the year of the delivery."
    )

    class Config:
        """
        Pydantic configuration class.
        `from_attributes = True` allows the model to be created from ORM objects.
        """

        from_attributes = True


class OilOverallStats(BaseModel):
    """
    Schema for overall oil consumption statistics.
    """

    total_volume: float = Field(
        ..., description="Total volume of oil delivered across all records in liters."
    )
    total_costs: float = Field(..., description="Total costs of all oil deliveries.")
    number_of_years: int = Field(
        ..., description="Total number of years covered by the oil data."
    )
    average_volume: float = Field(
        ..., description="Average annual oil volume usage in liters."
    )


class OilPriceTrend(BaseModel):
    """
    Schema for representing the oil price trend on a yearly basis.
    """

    year: int = Field(..., description="Year of the data point.")
    average_price: float = Field(
        ..., description="Average price per liter of oil for the given year."
    )


class OilYearlySummary(BaseModel):
    """
    Schema for a summary of oil data for a single year.
    """

    year: int = Field(..., description="Year of the summary.")
    total_volume: float = Field(
        ..., description="Total volume of oil delivered in the year in liters."
    )
    total_costs: float = Field(..., description="Total costs of oil for the year.")


class OilFillLevelsBase(BaseModel):
    """
    Base schema for an oil tank fill level measurement.
    """

    date: date_ = Field(..., description="Date of the fill level measurement.")
    level: float = Field(
        ..., description="Oil tank fill level in percentage (0.0 to 100.0)."
    )


class OilFillLevelsCreate(OilFillLevelsBase):
    """
    Schema for creating a new oil fill level record.
    """

    pass


class OilFillLevelsResponse(OilFillLevelsBase):
    """
    Schema for an oil fill level record retrieved from the database.
    """

    id: int = Field(..., description="Unique identifier for the fill level record.")

    class Config:
        """
        Pydantic configuration class.
        `from_attributes = True` allows the model to be created from ORM objects.
        """

        from_attributes = True


# --- Water Schemas ---
# This section defines the data models for water consumption and billing.


class WaterBase(BaseModel):
    """
    Base schema for a water bill record.
    """

    year: int = Field(..., description="Year of the water bill.")
    volume_water: int = Field(
        ..., description="Volume of tap water consumed in liters."
    )
    volume_wastewater: int = Field(..., description="Volume of wastewater in liters.")
    volume_rainwater: int = Field(..., description="Volume of rainwater in liters.")
    costs_water: float = Field(..., description="Total costs for tap water.")
    costs_wastewater: float = Field(..., description="Total costs for wastewater.")
    costs_rainwater: float = Field(..., description="Total costs for rainwater.")
    payments: float = Field(..., description="Total payments made for the water bill.")
    fixed_price: float = Field(
        ..., description="Fixed price component of the water bill."
    )
    note: Optional[str] = Field(
        None, description="Optional notes about the water bill."
    )


class WaterCreate(WaterBase):
    """
    Schema for creating a new water bill record.
    """

    pass


class WaterResponse(WaterBase):
    """
    Schema for a water bill record retrieved from the database.
    """

    id: int = Field(..., description="Unique identifier for the water record.")
    price_water: float = Field(
        ..., description="Calculated price per liter of tap water."
    )
    price_wastewater: float = Field(
        ..., description="Calculated price per liter of wastewater."
    )
    price_rainwater: float = Field(
        ..., description="Calculated price per liter of rainwater."
    )
    monthly_payment: float = Field(
        ..., description="Calculated average monthly payment for the year."
    )
    difference: float = Field(
        ...,
        description="Difference between total costs and total payments for the year.",
    )

    class Config:
        """
        Pydantic configuration class.
        `from_attributes = True` allows the model to be created from ORM objects.
        """

        from_attributes = True


class WaterOverallStats(BaseModel):
    """
    Schema for overall water consumption statistics.
    """

    total_volume: int = Field(
        ..., description="Total volume of tap water consumed across all records."
    )
    total_costs: float = Field(..., description="Total costs for all water bills.")
    number_of_years: int = Field(
        ..., description="Total number of years covered by the water data."
    )
    average_volume: float = Field(
        ..., description="Average annual tap water volume in liters."
    )


class WaterYearlySummary(BaseModel):
    """
    Schema for a summary of water data for a single year.
    """

    year: int = Field(..., description="Year of the summary.")
    volume_water: int = Field(
        ..., description="Total tap water volume for the year in liters."
    )
    volume_wastewater: int = Field(
        ..., description="Total wastewater volume for the year in liters."
    )
    costs_water: float = Field(
        ..., description="Total costs for tap water for the year."
    )
    costs_wastewater: float = Field(
        ..., description="Total costs for wastewater for the year."
    )


class WaterPriceTrend(BaseModel):
    """
    Schema for representing the water price trend on a yearly basis.
    """

    year: int = Field(..., description="Year of the data point.")
    price_water: float = Field(
        ..., description="Average price per liter of tap water for the year."
    )
    price_wastewater: float = Field(
        ..., description="Average price per liter of wastewater for the year."
    )
    price_rainwater: float = Field(
        ..., description="Average price per liter of rainwater for the year."
    )
    price_fixed: float = Field(..., description="Fixed price component for the year.")
