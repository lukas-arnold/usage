from sqlalchemy.orm import Session
from sqlalchemy import func, literal, and_, case, Float
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
    price_water = calculate_price(entry.costs_water, entry.volume_water)
    price_wastewater = calculate_price(entry.costs_wastewater, entry.volume_wastewater)
    price_rainwater = calculate_price(entry.costs_rainwater, entry.volume_rainwater)

    monthly_payment_water = calculate_monthly_payment(entry.payments_water)
    monthly_payment_wastewater = calculate_monthly_payment(entry.costs_wastewater)
    monthly_payment_rainwater = calculate_monthly_payment(entry.costs_rainwater)

    difference_water = calculate_difference(entry.payments_water, entry.costs_water)
    difference_wastewater = calculate_difference(
        entry.payments_wastewater, entry.costs_wastewater
    )
    difference_rainwater = calculate_difference(
        entry.payments_rainwater, entry.costs_rainwater
    )

    return {
        "price_water": round(price_water, 3),
        "price_wastewater": round(price_wastewater, 3),
        "price_rainwater": round(price_rainwater, 3),
        "monthly_payment_water": round(monthly_payment_water, 2),
        "monthly_payment_wastewater": round(monthly_payment_wastewater, 2),
        "monthly_payment_rainwater": round(monthly_payment_rainwater, 2),
        "difference_water": round(difference_water, 2),
        "difference_wastewater": round(difference_wastewater, 2),
        "difference_rainwater": round(difference_rainwater, 2),
    }


def get_water_overall_stats(db: Session) -> WaterOverallStats:
    total_volume_water = db.query(func.sum(WaterDB.volume_water)).scalar() or 0
    total_volume_wastewater = (
        db.query(func.sum(WaterDB.volume_wastewater)).scalar() or 0
    )
    total_volume_rainwater = db.query(func.sum(WaterDB.volume_rainwater)).scalar() or 0

    total_costs_water = db.query(func.sum(WaterDB.costs_water)).scalar() or 0
    total_costs_wastewater = db.query(func.sum(WaterDB.costs_wastewater)).scalar() or 0
    total_costs_rainwater = db.query(func.sum(WaterDB.costs_rainwater)).scalar() or 0

    total_payments_water = db.query(func.sum(WaterDB.payments_water)).scalar() or 0
    total_payments_wastewater = (
        db.query(func.sum(WaterDB.payments_wastewater)).scalar() or 0
    )
    total_payments_rainwater = (
        db.query(func.sum(WaterDB.payments_rainwater)).scalar() or 0
    )

    total_difference_water = calculate_difference(
        total_payments_water, total_costs_water
    )
    total_difference_wastewater = calculate_difference(
        total_payments_wastewater, total_costs_wastewater
    )
    total_difference_rainwater = calculate_difference(
        total_payments_rainwater, total_costs_rainwater
    )

    total_fixed_price = db.query(func.sum(WaterDB.fixed_price)).scalar() or 0

    number_of_years = db.query(func.count(func.distinct(WaterDB.year))).scalar() or 1

    average_yearly_volume_water = total_volume_water / number_of_years
    average_yearly_volume_wastewater = total_volume_wastewater / number_of_years
    average_yearly_volume_rainwater = total_volume_rainwater / number_of_years

    average_yearly_costs_water = total_costs_water / number_of_years
    average_yearly_costs_wastewater = total_costs_wastewater / number_of_years
    average_yearly_costs_rainwater = total_costs_rainwater / number_of_years

    average_yearly_fixed_price = total_fixed_price / number_of_years

    total_costs = (
        total_costs_water
        + total_costs_wastewater
        + total_costs_rainwater
        + total_fixed_price
    )
    average_usage = total_volume_water / number_of_years

    return WaterOverallStats(
        total_volume_water=round(total_volume_water, 2),
        total_volume_wastewater=round(total_volume_wastewater, 2),
        total_volume_rainwater=round(total_volume_rainwater, 2),
        total_costs_water=round(total_costs_water, 2),
        total_costs_wastewater=round(total_costs_wastewater, 2),
        total_costs_rainwater=round(total_costs_rainwater, 2),
        total_payments_water=round(total_payments_water, 2),
        total_payments_wastewater=round(total_payments_wastewater, 2),
        total_payments_rainwater=round(total_payments_rainwater, 2),
        total_difference_water=round(total_difference_water, 2),
        total_difference_wastewater=round(total_difference_wastewater, 2),
        total_difference_rainwater=round(total_difference_rainwater, 2),
        total_fixed_price=round(total_fixed_price, 2),
        number_of_years=number_of_years,
        average_yearly_volume_water=round(average_yearly_volume_water, 2),
        average_yearly_volume_wastewater=round(average_yearly_volume_wastewater, 2),
        average_yearly_volume_rainwater=round(average_yearly_volume_rainwater, 2),
        average_yearly_costs_water=round(average_yearly_costs_water, 2),
        average_yearly_costs_wastewater=round(average_yearly_costs_wastewater, 2),
        average_yearly_costs_rainwater=round(average_yearly_costs_rainwater, 2),
        average_yearly_fixed_price=round(average_yearly_fixed_price, 2),
        total_costs=round(total_costs, 2),
        average_usage=round(average_usage, 2),
    )


def get_water_price_trend(db: Session) -> List[WaterPriceTrend]:
    results = (
        db.query(
            WaterDB.year,
            func.avg(WaterDB.costs_water / WaterDB.volume_water).label(
                "average_price_water"
            ),
            func.min(
                case(
                    (
                        WaterDB.volume_water > 0,
                        WaterDB.costs_water / WaterDB.volume_water,
                    ),
                    else_=literal(None).cast(Float),
                )
            ).label("min_price_water"),
            func.max(WaterDB.costs_water / WaterDB.volume_water).label(
                "max_price_water"
            ),
            func.avg(WaterDB.costs_wastewater / WaterDB.volume_wastewater).label(
                "average_price_wastewater"
            ),
            func.min(
                case(
                    (
                        WaterDB.volume_wastewater > 0,
                        WaterDB.costs_wastewater / WaterDB.volume_water,
                    ),
                    else_=literal(None).cast(Float),
                )
            ).label("min_price_wastewater"),
            func.max(WaterDB.costs_wastewater / WaterDB.volume_wastewater).label(
                "max_price_wastewater"
            ),
            func.avg(WaterDB.costs_rainwater / WaterDB.volume_rainwater).label(
                "average_price_rainwater"
            ),
            func.min(
                case(
                    (
                        WaterDB.volume_rainwater > 0,
                        WaterDB.costs_rainwater / WaterDB.volume_rainwater,
                    ),
                    else_=literal(None).cast(Float),
                )
            ).label("min_price_rainwater"),
            func.max(WaterDB.costs_rainwater / WaterDB.volume_rainwater).label(
                "max_price_rainwater"
            ),
            func.avg(WaterDB.fixed_price).label("average_fixed_price"),
            func.min(WaterDB.fixed_price).label("min_fixed_price"),
            func.max(WaterDB.fixed_price).label("max_fixed_price"),
        )
        .filter(
            and_(
                WaterDB.volume_water > 0,
                WaterDB.volume_wastewater > 0,
                WaterDB.volume_rainwater > 0,
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
                average_price_water=round(r.average_price_water, 3),
                min_price_water=round(
                    (r.min_price_water if r.min_price_water is not None else 0.0),
                    3,
                ),
                max_price_water=round(r.max_price_water, 3),
                average_price_wastewater=round(r.average_price_wastewater, 3),
                min_price_wastewater=round(
                    (
                        r.min_price_wastewater
                        if r.min_price_wastewater is not None
                        else 0.0
                    ),
                    3,
                ),
                max_price_wastewater=round(
                    (
                        r.max_price_wastewater
                        if r.max_price_wastewater is not None
                        else 0.0
                    ),
                    3,
                ),
                average_price_rainwater=round(r.average_price_rainwater, 3),
                min_price_rainwater=(
                    round(r.min_price_rainwater, 3)
                    if r.min_price_rainwater is not None
                    else 0.0
                ),
                max_price_rainwater=(
                    round(r.max_price_rainwater, 3)
                    if r.max_price_rainwater is not None
                    else 0.0
                ),
                average_fixed_price=round(r.average_fixed_price, 3),
                min_fixed_price=(
                    round(r.min_fixed_price, 3)
                    if r.min_fixed_price is not None
                    else 0.0
                ),
                max_fixed_price=(
                    round(r.max_fixed_price, 3)
                    if r.max_fixed_price is not None
                    else 0.0
                ),
            )
        )
    return trends


def get_water_yearly_summary(db: Session) -> List[WaterYearlySummary]:
    results = (
        db.query(
            WaterDB.year,
            func.sum(WaterDB.volume_water).label("total_volume_water"),
            func.sum(WaterDB.volume_water).label("total_volume_wastewater"),
            func.sum(WaterDB.volume_rainwater).label("total_volume_rainwater"),
            func.sum(WaterDB.costs_water).label("total_costs_water"),
            func.sum(WaterDB.costs_wastewater).label("total_costs_wastewater"),
            func.sum(WaterDB.costs_rainwater).label("total_costs_rainwater"),
            func.sum(WaterDB.payments_water).label("total_payments_water"),
            func.sum(WaterDB.payments_wastewater).label("total_payments_wastewater"),
            func.sum(WaterDB.payments_rainwater).label("total_payments_rainwater"),
            func.sum(WaterDB.volume_water + WaterDB.volume_rainwater).label(
                "volume_wastewater"
            ),
            func.sum(WaterDB.costs_wastewater + WaterDB.costs_rainwater).label(
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
                total_volume_water=round(r.total_volume_water, 2),
                total_volume_wastewater=round(r.total_volume_wastewater, 2),
                total_volume_rainwater=round(r.total_volume_rainwater, 2),
                total_costs_water=round(r.total_costs_water, 2),
                total_costs_wastewater=round(r.total_costs_wastewater, 2),
                total_costs_rainwater=round(r.total_costs_rainwater, 2),
                total_payments_water=round(r.total_payments_water, 2),
                total_payments_wastewater=round(r.total_payments_wastewater, 2),
                total_payments_rainwater=round(r.total_payments_rainwater, 2),
                volume_wastewater=round(r.volume_wastewater, 2),
                costs_wastewater=round(r.costs_wastewater, 2),
            )
        )
    return summary
