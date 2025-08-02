from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case
from typing import List, Dict

from app.operations.operations import (
    create_entry,
    get_entry,
    get_entries,
    delete_entry,
    calculate_price,
    calculate_monthly_payment,
    calculate_difference,
)
from app.models import WaterDB
from app.schemas import (
    WaterCreate,
    WaterOverallStats,
    WaterYearlySummary,
    WaterPriceTrend,
)


def create_water_entry(db: Session, schema: WaterCreate):
    return create_entry(db, WaterDB, schema)


def get_water_entry(db: Session, entry_id: int):
    return get_entry(db, WaterDB, entry_id)


def get_water_entries(db: Session):
    return get_entries(db, WaterDB)


def delete_water_entry(db: Session, entry_id: int):
    return delete_entry(db, WaterDB, entry_id)


def calculate_water_derived_fields(entry: WaterDB) -> Dict[str, float]:
    costs = (
        entry.costs_water
        + entry.costs_wastewater
        + entry.costs_rainwater
        + entry.fixed_price
    )

    price_water = calculate_price(entry.costs_water, entry.volume_water)
    price_wastewater = calculate_price(entry.costs_wastewater, entry.volume_wastewater)
    price_rainwater = calculate_price(entry.costs_rainwater, entry.volume_rainwater)

    monthly_payment = calculate_monthly_payment(entry.payments)
    difference = calculate_difference(costs, entry.payments)

    return {
        "costs": round(costs, 2),
        "price_water": round(price_water, 3),
        "price_wastewater": round(price_wastewater, 3),
        "price_rainwater": round(price_rainwater, 3),
        "monthly_payment": round(monthly_payment, 2),
        "difference": round(-difference, 2),
    }


def get_water_overall_stats(db: Session) -> WaterOverallStats:
    total_costs_water = db.query(func.sum(WaterDB.costs_water)).scalar() or 0
    total_costs_wastewater = db.query(func.sum(WaterDB.costs_wastewater)).scalar() or 0
    total_costs_rainwater = db.query(func.sum(WaterDB.costs_rainwater)).scalar() or 0
    total_fixed_price = db.query(func.sum(WaterDB.fixed_price)).scalar() or 0

    total_volume = db.query(func.sum(WaterDB.volume_water)).scalar() or 0
    total_costs = (
        total_costs_water
        + total_costs_wastewater
        + total_costs_rainwater
        + total_fixed_price
    )
    number_of_years = db.query(func.count(func.distinct(WaterDB.year))).scalar() or 1
    average_volume = total_volume / number_of_years

    return WaterOverallStats(
        total_volume=total_volume,
        number_of_years=number_of_years,
        total_costs=round(total_costs, 2),
        average_volume=round(average_volume, 2),
    )


def get_water_price_trend(db: Session) -> List[WaterPriceTrend]:
    results = (
        db.query(
            WaterDB.year,
            func.avg(WaterDB.costs_water / WaterDB.volume_water).label("price_water"),
            func.avg(WaterDB.costs_wastewater / WaterDB.volume_wastewater).label(
                "price_wastewater"
            ),
            # Use a CASE statement to handle division by zero
            # If volume_rainwater is 0 or less, the result is null. Otherwise, perform the division.
            func.avg(
                case(
                    (
                        WaterDB.volume_rainwater > 0,
                        WaterDB.costs_rainwater / WaterDB.volume_rainwater,
                    )
                )
            ).label("price_rainwater"),
            func.avg(WaterDB.fixed_price).label("price_fixed"),
        )
        .filter(
            # Only filter out years where the primary data is missing.
            and_(
                WaterDB.volume_water > 0,
                WaterDB.volume_wastewater > 0,
            )
        )
        .group_by(WaterDB.year)
        .order_by(WaterDB.year)
        .all()
    )
    trends = []
    for r in results:
        trends.append(
            WaterPriceTrend(
                year=int(r.year),
                price_water=round(r.price_water, 3),
                price_wastewater=round(r.price_wastewater, 3),
                # The rainwater price will be None if the volume was 0
                price_rainwater=(
                    round(r.price_rainwater, 3)
                    if r.price_rainwater is not None
                    else None
                ),
                price_fixed=r.price_fixed,
            )
        )
    return trends


def get_water_yearly_summary(db: Session) -> List[WaterYearlySummary]:
    results = (
        db.query(
            WaterDB.year,
            WaterDB.volume_water,
            WaterDB.costs_water,
            (WaterDB.volume_water + WaterDB.volume_rainwater).label(
                "volume_wastewater"
            ),
            (WaterDB.costs_wastewater + WaterDB.costs_rainwater).label(
                "costs_wastewater"
            ),
        )
        .group_by(WaterDB.year)
        .order_by(WaterDB.year)
        .all()
    )
    summary = []
    for r in results:
        summary.append(
            WaterYearlySummary(
                year=int(r.year),
                volume_water=r.volume_water,
                costs_water=r.costs_water,
                volume_wastewater=r.volume_wastewater,
                costs_wastewater=r.costs_wastewater,
            )
        )
    return summary
