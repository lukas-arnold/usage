from sqlalchemy.orm import Session
from sqlalchemy import func, literal, and_
from datetime import date
from typing import Type, TypeVar, List, Dict, Union, Optional
import math

from . import models, schemas

ModelType = TypeVar("ModelType", bound=models.Base)


def create_entry(
    db: Session,
    model: Type[ModelType],
    entry_schema: Union[
        schemas.ElectricityCreate, schemas.OilCreate, schemas.WaterCreate
    ],
) -> ModelType:
    db_entry = model(**entry_schema.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def get_entry(
    db: Session, model: Type[ModelType], entry_id: int
) -> Optional[ModelType]:
    return db.query(model).filter(model.id == entry_id).first()


def get_entries(db: Session, model: Type[ModelType]) -> List[ModelType]:
    return db.query(model).all()


def delete_entry(db: Session, model: Type[ModelType], entry_id: int) -> bool:
    db_entry = db.query(model).filter(model.id == entry_id).first()
    if db_entry:
        db.delete(db_entry)
        db.commit()
        return True
    return False


def calculate_electricity_derived_fields(
    entry: models.ElectricityDB,
) -> Dict[str, float]:
    price_per_kwh = 0.0
    if entry.usage != 0:
        price_per_kwh = entry.costs / entry.usage

    time_from = entry.time_from
    time_to = entry.time_to

    duration_days = (time_to - time_from).days
    if duration_days <= 0:
        duration_days = 1

    monthly_payment = 0.0
    if duration_days > 0:
        monthly_payment = (entry.payments / duration_days) * (365.25 / 12)

    difference = entry.costs - entry.payments

    return {
        "price": round(price_per_kwh, 3),
        "monthly_payment": round(monthly_payment, 2),
        "difference": round(difference, 2),
    }


def get_electricity_overall_stats(db: Session) -> schemas.ElectricityOverallStats:
    results = db.query(
        func.sum(models.ElectricityDB.usage).label("total_usage"),
        func.sum(models.ElectricityDB.costs).label("total_costs"),
        func.count(
            func.distinct(func.strftime("%Y", models.ElectricityDB.time_from))
        ).label("number_of_years"),
    ).first()

    total_usage = results.total_usage if results.total_usage is not None else 0
    total_costs = results.total_costs if results.total_costs is not None else 0
    number_of_years = (
        results.number_of_years if results.number_of_years is not None else 0
    )

    average_yearly_usage = 0
    if number_of_years > 0:
        average_yearly_usage = total_usage / number_of_years

    return schemas.ElectricityOverallStats(
        total_usage=round(total_usage, 2),
        total_costs=round(total_costs, 2),
        number_of_years=number_of_years,
        average_yearly_usage=round(average_yearly_usage, 2),
    )


def get_electricity_price_trend(db: Session) -> List[schemas.ElectricityPriceTrend]:
    subquery = (
        db.query(
            func.strftime("%Y", models.ElectricityDB.time_from).label("year"),
            (models.ElectricityDB.costs / models.ElectricityDB.usage).label(
                "price_per_kwh"
            ),
        )
        .filter(models.ElectricityDB.usage != literal(0))
        .subquery()
    )

    results = (
        db.query(
            subquery.c.year,
            func.avg(subquery.c.price_per_kwh).label("average_price"),
            func.min(subquery.c.price_per_kwh).label("min_price"),
            func.max(subquery.c.price_per_kwh).label("max_price"),
        )
        .group_by(subquery.c.year)
        .order_by(subquery.c.year)
        .all()
    )

    trends = []
    for r in results:
        trends.append(
            schemas.ElectricityPriceTrend(
                year=int(r.year),
                average_price=round(r.average_price, 3),
                min_price=round(r.min_price, 3),
                max_price=round(r.max_price, 3),
            )
        )
    return trends


def calculate_oil_derived_fields(db: Session, entry: models.OilDB) -> Dict[str, float]:
    price_per_liter = 0.0
    if entry.volume != 0:
        price_per_liter = entry.costs / entry.volume

    year = entry.date.year
    yearly_data = (
        db.query(
            func.sum(models.OilDB.volume).label("year_usage"),
            func.sum(models.OilDB.costs).label("year_costs"),
        )
        .filter(func.strftime("%Y", models.OilDB.date) == str(year))
        .first()
    )

    year_usage = yearly_data.year_usage if yearly_data.year_usage is not None else 0
    year_costs = yearly_data.year_costs if yearly_data.year_costs is not None else 0

    return {
        "price": round(price_per_liter, 3),
        "year_usage": round(year_usage, 2),
        "year_costs": round(year_costs, 2),
        "year": year,
    }


def get_oil_overall_stats(db: Session) -> schemas.OilOverallStats:
    results = db.query(
        func.sum(models.OilDB.volume).label("total_volume"),
        func.sum(models.OilDB.costs).label("total_costs"),
        func.count(func.distinct(func.strftime("%Y", models.OilDB.date))).label(
            "number_of_years"
        ),
    ).first()

    total_volume = results.total_volume if results.total_volume is not None else 0
    total_costs = results.total_costs if results.total_costs is not None else 0
    number_of_years = (
        results.number_of_years if results.number_of_years is not None else 0
    )

    average_yearly_volume = 0
    if number_of_years > 0:
        average_yearly_volume = total_volume / number_of_years

    return schemas.OilOverallStats(
        total_volume=round(total_volume, 2),
        total_costs=round(total_costs, 2),
        number_of_years=number_of_years,
        average_yearly_volume=round(average_yearly_volume, 2),
    )


def get_oil_price_trend(db: Session) -> List[schemas.OilPriceTrend]:
    subquery = (
        db.query(
            func.strftime("%Y", models.OilDB.date).label("year"),
            (models.OilDB.costs / models.OilDB.volume).label("price_per_liter"),
        )
        .filter(models.OilDB.volume != literal(0))
        .subquery()
    )

    results = (
        db.query(
            subquery.c.year,
            func.avg(subquery.c.price_per_liter).label("average_price"),
            func.min(subquery.c.price_per_liter).label("min_price"),
            func.max(subquery.c.price_per_liter).label("max_price"),
        )
        .group_by(subquery.c.year)
        .order_by(subquery.c.year)
        .all()
    )

    trends = []
    for r in results:
        trends.append(
            schemas.OilPriceTrend(
                year=int(r.year),
                average_price=round(r.average_price, 3),
                min_price=round(r.min_price, 3),
                max_price=round(r.max_price, 3),
            )
        )
    return trends


def calculate_water_derived_fields(entry: models.WaterDB) -> Dict[str, float]:
    price_per_m3_water = 0.0
    if entry.volume_consumed_water != 0:
        price_per_m3_water = entry.costs_water / entry.volume_consumed_water

    price_per_m3_wastewater = 0.0
    if entry.volume_consumed_water != 0:
        price_per_m3_wastewater = entry.costs_wastewater / entry.volume_consumed_water

    monthly_payment_water = entry.payments_water / 12
    monthly_payment_wastewater = entry.payments_wastewater / 12

    difference_water = entry.costs_water - entry.payments_water
    difference_wastewater = entry.costs_wastewater - entry.payments_wastewater

    return {
        "price_per_m3_water": round(price_per_m3_water, 3),
        "price_per_m3_wastewater": round(price_per_m3_wastewater, 3),
        "monthly_payment_water": round(monthly_payment_water, 2),
        "monthly_payment_wastewater": round(monthly_payment_wastewater, 2),
        "difference_water": round(difference_water, 2),
        "difference_wastewater": round(difference_wastewater, 2),
    }


def get_water_overall_stats(db: Session) -> schemas.WaterOverallStats:
    results = db.query(
        func.sum(models.WaterDB.volume_consumed_water).label(
            "total_volume_consumed_water"
        ),
        func.sum(models.WaterDB.costs_water).label("total_costs_water"),
        func.sum(models.WaterDB.costs_wastewater).label("total_costs_wastewater"),
        func.sum(models.WaterDB.volume_rainwater).label("total_volume_rainwater"),
        func.sum(models.WaterDB.costs_rainwater).label("total_costs_rainwater"),
        func.sum(models.WaterDB.payments_water).label("total_payments_water"),
        func.sum(models.WaterDB.payments_wastewater).label("total_payments_wastewater"),
        func.count(func.distinct(models.WaterDB.year)).label("number_of_years"),
    ).first()

    total_volume_consumed_water = (
        results.total_volume_consumed_water
        if results.total_volume_consumed_water is not None
        else 0
    )
    total_costs_water = (
        results.total_costs_water if results.total_costs_water is not None else 0
    )
    total_costs_wastewater = (
        results.total_costs_wastewater
        if results.total_costs_wastewater is not None
        else 0
    )
    total_volume_rainwater = (
        results.total_volume_rainwater
        if results.total_volume_rainwater is not None
        else 0
    )
    total_costs_rainwater = (
        results.total_costs_rainwater
        if results.total_costs_rainwater is not None
        else 0
    )
    total_payments_water = (
        results.total_payments_water if results.total_payments_water is not None else 0
    )
    total_payments_wastewater = (
        results.total_payments_wastewater
        if results.total_payments_wastewater is not None
        else 0
    )
    number_of_years = (
        results.number_of_years if results.number_of_years is not None else 0
    )

    average_yearly_volume_consumed_water = 0
    if number_of_years > 0:
        average_yearly_volume_consumed_water = (
            total_volume_consumed_water / number_of_years
        )

    average_yearly_volume_rainwater = 0  # Calculation for new field
    if number_of_years > 0:
        average_yearly_volume_rainwater = total_volume_rainwater / number_of_years

    total_difference_water = total_costs_water - total_payments_water
    total_difference_wastewater = total_costs_wastewater - total_payments_wastewater

    return schemas.WaterOverallStats(
        total_volume_consumed_water=round(total_volume_consumed_water, 2),
        total_costs_water=round(total_costs_water, 2),
        total_costs_wastewater=round(total_costs_wastewater, 2),
        total_volume_rainwater=round(total_volume_rainwater, 2),
        total_costs_rainwater=round(total_costs_rainwater, 2),
        total_payments_water=round(total_payments_water, 2),
        total_payments_wastewater=round(total_payments_wastewater, 2),
        total_difference_water=round(total_difference_water, 2),
        total_difference_wastewater=round(total_difference_wastewater, 2),
        number_of_years=number_of_years,
        average_yearly_volume_consumed_water=round(
            average_yearly_volume_consumed_water, 2
        ),
        average_yearly_volume_rainwater=round(
            average_yearly_volume_rainwater, 2
        ),  # Include new field
    )


def get_water_price_trend(db: Session) -> List[schemas.WaterPriceTrend]:
    subquery_water = (
        db.query(
            models.WaterDB.year,
            (models.WaterDB.costs_water / models.WaterDB.volume_consumed_water).label(
                "price_per_m3_water"
            ),
        )
        .filter(models.WaterDB.volume_consumed_water != literal(0))
        .subquery()
    )

    subquery_wastewater = (
        db.query(
            models.WaterDB.year,
            (
                models.WaterDB.costs_wastewater / models.WaterDB.volume_consumed_water
            ).label("price_per_m3_wastewater"),
        )
        .filter(models.WaterDB.volume_consumed_water != literal(0))
        .subquery()
    )

    results = (
        db.query(
            func.coalesce(subquery_water.c.year, subquery_wastewater.c.year).label(
                "year"
            ),
            func.avg(subquery_water.c.price_per_m3_water).label(
                "average_price_per_m3_water"
            ),
            func.min(subquery_water.c.price_per_m3_water).label(
                "min_price_per_m3_water"
            ),
            func.max(subquery_water.c.price_per_m3_water).label(
                "max_price_per_m3_water"
            ),
            func.avg(subquery_wastewater.c.price_per_m3_wastewater).label(
                "average_price_per_m3_wastewater"
            ),
            func.min(subquery_wastewater.c.price_per_m3_wastewater).label(
                "min_price_per_m3_wastewater"
            ),
            func.max(subquery_wastewater.c.price_per_m3_wastewater).label(
                "max_price_per_m3_wastewater"
            ),
        )
        .outerjoin(
            subquery_wastewater, subquery_water.c.year == subquery_wastewater.c.year
        )
        .group_by("year")
        .order_by("year")
        .all()
    )

    trends = []
    for r in results:
        trends.append(
            schemas.WaterPriceTrend(
                year=int(r.year),
                average_price_per_m3_water=(
                    round(r.average_price_per_m3_water, 3)
                    if r.average_price_per_m3_water is not None
                    else 0.0
                ),
                min_price_per_m3_water=(
                    round(r.min_price_per_m3_water, 3)
                    if r.min_price_per_m3_water is not None
                    else 0.0
                ),
                max_price_per_m3_water=(
                    round(r.max_price_per_m3_water, 3)
                    if r.max_price_per_m3_water is not None
                    else 0.0
                ),
                average_price_per_m3_wastewater=(
                    round(r.average_price_per_m3_wastewater, 3)
                    if r.average_price_per_m3_wastewater is not None
                    else 0.0
                ),
                min_price_per_m3_wastewater=(
                    round(r.min_price_per_m3_wastewater, 3)
                    if r.min_price_per_m3_wastewater is not None
                    else 0.0
                ),
                max_price_per_m3_wastewater=(
                    round(r.max_price_per_m3_wastewater, 3)
                    if r.max_price_per_m3_wastewater is not None
                    else 0.0
                ),
            )
        )
    return trends
