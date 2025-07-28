from sqlalchemy.orm import Session
from sqlalchemy import func
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
from app.models import ElectricityDB
from app.schemas import (
    ElectricityCreate,
    ElectricityOverallStats,
    ElectricityYearlySummary,
    ElectricityPriceTrend,
)


def create_electricity_entry(db: Session, schema: ElectricityCreate):
    return create_entry(db, ElectricityDB, schema)


def get_electricity_entry(db: Session, entry_id: int):
    return get_entry(db, ElectricityDB, entry_id)


def get_electricity_entries(db: Session):
    return get_entries(db, ElectricityDB)


def delete_electricity_entry(db: Session, entry_id: int):
    return delete_entry(db, ElectricityDB, entry_id)


def calculate_electricity_derived_fields(
    entry: ElectricityDB,
) -> Dict[str, float]:
    price = calculate_price(entry.costs, entry.usage)
    monthly_payment = calculate_monthly_payment(entry.payments)
    difference = calculate_difference(entry.payments, entry.costs)
    return {
        "price": round(price, 3),
        "monthly_payment": round(monthly_payment, 2),
        "difference": round(difference, 2),
    }


def get_electricity_overall_stats(db: Session) -> ElectricityOverallStats:
    total_usage = db.query(func.sum(ElectricityDB.usage)).scalar() or 0
    total_costs = db.query(func.sum(ElectricityDB.costs)).scalar() or 0
    number_of_years = (
        db.query(
            func.count(func.distinct(func.strftime("%Y", ElectricityDB.time_from)))
        ).scalar()
        or 1
    )
    average_yearly_usage = total_usage / number_of_years
    return ElectricityOverallStats(
        total_usage=round(total_usage, 2),
        total_costs=round(total_costs, 2),
        number_of_years=number_of_years,
        average_yearly_usage=round(average_yearly_usage, 2),
    )


def get_electricity_yearly_summary(
    db: Session,
) -> List[ElectricityYearlySummary]:
    results = (
        db.query(
            func.strftime("%Y", ElectricityDB.time_from).label("year"),
            func.sum(ElectricityDB.usage).label("total_usage"),
            func.sum(ElectricityDB.costs).label("total_costs"),
        )
        .group_by("year")
        .order_by("year")
        .all()
    )
    summary = []
    for r in results:
        summary.append(
            ElectricityYearlySummary(
                year=int(r.year),
                total_usage=round(r.total_usage, 2),
                total_costs=round(r.total_costs, 2),
            )
        )
    return summary


def get_electricity_price_trend(db: Session) -> List[ElectricityPriceTrend]:
    results = (
        db.query(
            func.strftime("%Y", ElectricityDB.time_from).label("year"),
            func.avg(ElectricityDB.costs / ElectricityDB.usage).label("average_price"),
            func.min(ElectricityDB.costs / ElectricityDB.usage).label("min_price"),
            func.max(ElectricityDB.costs / ElectricityDB.usage).label("max_price"),
        )
        .filter(ElectricityDB.usage > 0)
        .group_by("year")
        .order_by("year")
        .all()
    )
    trends = []
    for r in results:
        trends.append(
            ElectricityPriceTrend(
                year=int(r.year),
                average_price=round(r.average_price, 3),
                min_price=round(r.min_price, 3),
                max_price=round(r.max_price, 3),
            )
        )
    return trends
