# your_project/crud.py
from sqlalchemy.orm import Session
from typing import Type, Union, Dict, Any, List
from sqlalchemy import func, extract, and_
from datetime import datetime, date, timedelta

# Import literal for potential linter appeasement in filters
from sqlalchemy.sql import literal

from .models import ElectricityDB, OilDB, WaterDB
from .schemas import (
    ElectricityCreate,
    OilCreate,
    WaterCreate,
    ElectricityOverallStats,
    ElectricityPriceTrend,
    OilOverallStats,
    OilPriceTrend,
    WaterOverallStats,
    WaterPriceTrend,
)


# --- Generic CRUD Operations ---


def create_entry(
    db: Session,
    model: Type[Union[ElectricityDB, OilDB, WaterDB]],
    schema: Union[ElectricityCreate, OilCreate, WaterCreate],
):
    db_entry = model(**schema.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def get_entry(
    db: Session, model: Type[Union[ElectricityDB, OilDB, WaterDB]], entry_id: int
):
    return db.query(model).filter(model.id == entry_id).first()


def get_entries(db: Session, model: Type[Union[ElectricityDB, OilDB, WaterDB]]):
    return db.query(model).all()


def delete_entry(
    db: Session, model: Type[Union[ElectricityDB, OilDB, WaterDB]], entry_id: int
):
    db_entry = db.query(model).filter(model.id == entry_id).first()
    if db_entry:
        db.delete(db_entry)
        db.commit()
        return True
    return False


# --- Utility Functions for Derived Fields (for *Response schemas) ---


def calculate_electricity_derived_fields(entry: ElectricityDB) -> Dict[str, Any]:
    # Ensure explicit float conversion for division and safe check for zero
    price = entry.costs / float(entry.usage) if entry.usage != 0 else 0

    time_from = entry.time_from
    time_to = entry.time_to

    days_duration = float((time_to - time_from).days)
    months_duration = days_duration / 30.4375 if days_duration > 0 else 0

    monthly_payment = entry.payments / months_duration if months_duration > 0 else 0
    difference = entry.payments - entry.costs

    return {
        "price": round(float(price), 3),
        "monthly_payment": round(float(monthly_payment), 2),
        "difference": round(float(difference), 2),
    }


def calculate_oil_derived_fields(db: Session, entry: OilDB) -> Dict[str, Any]:
    # Ensure explicit float conversion for division and safe check for zero
    price = entry.costs / float(entry.volume) if entry.volume != 0 else 0

    year_stats = (
        db.query(
            func.sum(OilDB.volume).label("yearly_volume"),
            func.sum(OilDB.costs).label("yearly_costs"),
        )
        .filter(extract("year", OilDB.date) == entry.date.year)
        .first()
    )

    year_usage = (
        year_stats.yearly_volume
        if year_stats and year_stats.yearly_volume is not None
        else 0
    )
    year_costs = (
        year_stats.yearly_costs
        if year_stats and year_stats.yearly_costs is not None
        else 0
    )

    return {
        "price": round(float(price), 3),
        "year_usage": round(float(year_usage), 2),
        "year_costs": round(float(year_costs), 2),
        "year": entry.date.year,
    }


def calculate_water_derived_fields(entry: WaterDB) -> Dict[str, Any]:
    # Ensure explicit float conversion for division and safe check for zero
    price_water = (
        entry.costs_water / float(entry.volume_consumed_water)
        if entry.volume_consumed_water != 0
        else 0
    )
    price_wastewater = (
        entry.costs_wastewater / float(entry.volume_consumed_water)
        if entry.volume_consumed_water != 0
        else 0
    )
    price_rainwater = (
        entry.costs_rainwater / float(entry.volume_rainwater)
        if entry.volume_rainwater != 0
        else 0
    )

    total_costs = entry.costs_water + entry.costs_wastewater + entry.costs_rainwater

    return {
        "price_water": round(float(price_water), 3),
        "price_wastewater": round(float(price_wastewater), 3),
        "price_rainwater": round(float(price_rainwater), 3),
        "total_costs": round(float(total_costs), 2),
    }


# --- Statistics Functions ---


# Electricity Statistics
def get_electricity_overall_stats(db: Session) -> ElectricityOverallStats:
    total_stats = db.query(
        func.sum(ElectricityDB.usage).label("total_usage"),
        func.sum(ElectricityDB.costs).label("total_costs"),
        func.count(func.distinct(extract("year", ElectricityDB.time_from))).label(
            "number_of_years"
        ),
    ).first()

    if total_stats and total_stats.total_usage is not None:
        average_yearly_usage = (
            float(total_stats.total_usage) / total_stats.number_of_years
            if total_stats.number_of_years > 0
            else 0
        )
        return ElectricityOverallStats(
            total_usage=round(float(total_stats.total_usage), 2),
            total_costs=round(float(total_stats.total_costs), 2),
            number_of_years=total_stats.number_of_years,
            average_yearly_usage=round(float(average_yearly_usage), 2),
        )
    return ElectricityOverallStats(
        total_usage=0.0, total_costs=0.0, number_of_years=0, average_yearly_usage=0.0
    )


def get_electricity_price_trend(db: Session) -> List[ElectricityPriceTrend]:
    yearly_data = (
        db.query(
            extract("year", ElectricityDB.time_from).label("year"),
            func.avg(ElectricityDB.costs / ElectricityDB.usage).label("average_price"),
            func.min(ElectricityDB.costs / ElectricityDB.usage).label("min_price"),
            func.max(ElectricityDB.costs / ElectricityDB.usage).label("max_price"),
        )
        .filter(
            ElectricityDB.usage != literal(0),  # Use literal to appease some linters
        )
        .group_by("year")
        .order_by("year")
        .all()
    )

    trend = []
    for data in yearly_data:
        trend.append(
            ElectricityPriceTrend(
                year=int(data.year),
                average_price=(
                    round(float(data.average_price), 3)
                    if data.average_price is not None
                    else 0
                ),
                min_price=(
                    round(float(data.min_price), 3) if data.min_price is not None else 0
                ),
                max_price=(
                    round(float(data.max_price), 3) if data.max_price is not None else 0
                ),
            )
        )
    return trend


# Oil Statistics
def calculate_yearly_stats_oil(db: Session, year: int) -> Dict[str, Any]:
    stats = (
        db.query(
            func.sum(OilDB.volume).label("yearly_volume"),
            func.sum(OilDB.costs).label("yearly_costs"),
            func.count(OilDB.id).label("number_of_entries"),
        )
        .filter(extract("year", OilDB.date) == year)
        .first()
    )

    if stats and stats.yearly_volume is not None:
        average_price = (
            stats.yearly_costs / float(stats.yearly_volume)
            if stats.yearly_volume != 0
            else 0
        )
        return {
            "yearly_volume": round(float(stats.yearly_volume), 2),
            "yearly_costs": round(float(stats.yearly_costs), 2),
            "number_of_entries": stats.number_of_entries,
            "average_price": round(float(average_price), 3),
        }
    return {
        "yearly_volume": 0.0,
        "yearly_costs": 0.0,
        "number_of_entries": 0,
        "average_price": 0.0,
    }


def get_oil_overall_stats(db: Session) -> OilOverallStats:
    total_stats = db.query(
        func.sum(OilDB.volume).label("total_volume"),
        func.sum(OilDB.costs).label("total_costs"),
        func.count(func.distinct(extract("year", OilDB.date))).label("number_of_years"),
    ).first()

    if total_stats and total_stats.total_volume is not None:
        average_yearly_volume = (
            float(total_stats.total_volume) / total_stats.number_of_years
            if total_stats.number_of_years > 0
            else 0
        )
        return OilOverallStats(
            total_volume=round(float(total_stats.total_volume), 2),
            total_costs=round(float(total_stats.total_costs), 2),
            number_of_years=total_stats.number_of_years,
            average_yearly_volume=round(float(average_yearly_volume), 2),
        )
    return OilOverallStats(
        total_volume=0.0, total_costs=0.0, number_of_years=0, average_yearly_volume=0.0
    )


def get_oil_price_trend(db: Session) -> List[OilPriceTrend]:
    yearly_data = (
        db.query(
            extract("year", OilDB.date).label("year"),
            func.avg(OilDB.costs / OilDB.volume).label("average_price"),
            func.min(OilDB.costs / OilDB.volume).label("min_price"),
            func.max(OilDB.costs / OilDB.volume).label("max_price"),
        )
        .filter(
            OilDB.volume != literal(0),  # Use literal to appease some linters
        )
        .group_by("year")
        .order_by("year")
        .all()
    )

    trend = []
    for data in yearly_data:
        trend.append(
            OilPriceTrend(
                year=int(data.year),
                average_price=(
                    round(float(data.average_price), 3)
                    if data.average_price is not None
                    else 0
                ),
                min_price=(
                    round(float(data.min_price), 3) if data.min_price is not None else 0
                ),
                max_price=(
                    round(float(data.max_price), 3) if data.max_price is not None else 0
                ),
            )
        )
    return trend


# Water Statistics
def get_water_overall_stats(db: Session) -> WaterOverallStats:
    total_stats = db.query(
        func.sum(WaterDB.volume_consumed_water).label("total_volume_consumed_water"),
        func.sum(WaterDB.volume_rainwater).label("total_volume_rainwater"),
        func.sum(WaterDB.costs_water).label("total_costs_water"),
        func.sum(WaterDB.costs_wastewater).label("total_costs_wastewater"),
        func.sum(WaterDB.costs_rainwater).label("total_costs_rainwater"),
        func.count(func.distinct(WaterDB.year)).label("number_of_years"),
    ).first()

    if total_stats and total_stats.total_volume_consumed_water is not None:
        num_years = (
            total_stats.number_of_years if total_stats.number_of_years > 0 else 1
        )

        avg_vol_consumed = float(total_stats.total_volume_consumed_water) / num_years
        avg_vol_rainwater = float(total_stats.total_volume_rainwater) / num_years
        avg_costs_water = total_stats.total_costs_water / num_years
        avg_costs_wastewater = total_stats.total_costs_wastewater / num_years
        avg_costs_rainwater = total_stats.total_costs_rainwater / num_years

        return WaterOverallStats(
            total_volume_consumed_water=round(
                float(total_stats.total_volume_consumed_water), 2
            ),
            total_volume_rainwater=round(float(total_stats.total_volume_rainwater), 2),
            total_costs_water=round(float(total_stats.total_costs_water), 2),
            total_costs_wastewater=round(float(total_stats.total_costs_wastewater), 2),
            total_costs_rainwater=round(float(total_stats.total_costs_rainwater), 2),
            number_of_years=total_stats.number_of_years,
            average_yearly_volume_consumed_water=round(float(avg_vol_consumed), 2),
            average_yearly_volume_rainwater=round(float(avg_vol_rainwater), 2),
            average_yearly_costs_water=round(float(avg_costs_water), 2),
            average_yearly_costs_wastewater=round(float(avg_costs_wastewater), 2),
            average_yearly_costs_rainwater=round(float(avg_costs_rainwater), 2),
        )
    return WaterOverallStats(
        total_volume_consumed_water=0.0,
        total_volume_rainwater=0.0,
        total_costs_water=0.0,
        total_costs_wastewater=0.0,
        total_costs_rainwater=0.0,
        number_of_years=0,
        average_yearly_volume_consumed_water=0.0,
        average_yearly_volume_rainwater=0.0,
        average_yearly_costs_water=0.0,
        average_yearly_costs_wastewater=0.0,
        average_yearly_costs_rainwater=0.0,
    )


def get_water_price_trend(db: Session) -> List[WaterPriceTrend]:
    trend_data = (
        db.query(
            WaterDB.year,
            func.avg(WaterDB.costs_water / WaterDB.volume_consumed_water).label(
                "average_price_water"
            ),
            func.avg(WaterDB.costs_wastewater / WaterDB.volume_consumed_water).label(
                "average_price_wastewater"
            ),
            func.avg(WaterDB.costs_rainwater / WaterDB.volume_rainwater).label(
                "average_price_rainwater"
            ),
            func.min(WaterDB.costs_water / WaterDB.volume_consumed_water).label(
                "min_price_water"
            ),
            func.max(WaterDB.costs_water / WaterDB.volume_consumed_water).label(
                "max_price_water"
            ),
            func.min(WaterDB.costs_wastewater / WaterDB.volume_consumed_water).label(
                "min_price_wastewater"
            ),
            func.max(WaterDB.costs_wastewater / WaterDB.volume_consumed_water).label(
                "max_price_wastewater"
            ),
            func.min(WaterDB.costs_rainwater / WaterDB.volume_rainwater).label(
                "min_price_rainwater"
            ),
            func.max(WaterDB.costs_rainwater / WaterDB.volume_rainwater).label(
                "max_price_rainwater"
            ),
        )
        .filter(
            and_(
                WaterDB.volume_consumed_water
                != literal(0),  # Use literal to appease some linters
                WaterDB.volume_rainwater
                != literal(0),  # Use literal to appease some linters
            )
        )
        .group_by(WaterDB.year)
        .order_by(WaterDB.year)
        .all()
    )

    trend = []
    for data in trend_data:
        trend.append(
            WaterPriceTrend(
                year=int(data.year),
                average_price_water=(
                    round(float(data.average_price_water), 3)
                    if data.average_price_water is not None
                    else 0
                ),
                average_price_wastewater=(
                    round(float(data.average_price_wastewater), 3)
                    if data.average_price_wastewater is not None
                    else 0
                ),
                average_price_rainwater=(
                    round(float(data.average_price_rainwater), 3)
                    if data.average_price_rainwater is not None
                    else 0
                ),
                min_price_water=(
                    round(float(data.min_price_water), 3)
                    if data.min_price_water is not None
                    else 0
                ),
                max_price_water=(
                    round(float(data.max_price_water), 3)
                    if data.max_price_water is not None
                    else 0
                ),
                min_price_wastewater=(
                    round(float(data.min_price_wastewater), 3)
                    if data.min_price_wastewater is not None
                    else 0
                ),
                max_price_wastewater=(
                    round(float(data.max_price_wastewater), 3)
                    if data.max_price_wastewater is not None
                    else 0
                ),
                min_price_rainwater=(
                    round(float(data.min_price_rainwater), 3)
                    if data.min_price_rainwater is not None
                    else 0
                ),
                max_price_rainwater=(
                    round(float(data.max_price_rainwater), 3)
                    if data.max_price_rainwater is not None
                    else 0
                ),
            )
        )
    return trend
