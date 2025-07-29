from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict

from app.operations.operations import (
    create_entry,
    get_entry,
    get_entries,
    delete_entry,
    calculate_price,
)
from app.models import OilDB, OilFillLevelDB
from app.schemas import (
    OilCreate,
    OilOverallStats,
    OilYearlySummary,
    OilPriceTrend,
    OilFillLevelsCreate,
)


def create_oil_entry(db: Session, schema: OilCreate):
    return create_entry(db, OilDB, schema)


def get_oil_entry(db: Session, entry_id: int):
    return get_entry(db, OilDB, entry_id)


def get_oil_entries(db: Session):
    return get_entries(db, OilDB)


def delete_oil_entry(db: Session, entry_id: int):
    return delete_entry(db, OilDB, entry_id)


def calculate_oil_derived_fields(
    entry: OilDB,
) -> Dict[str, float]:
    price = calculate_price(entry.costs, entry.volume)
    year_usage = float(entry.volume)
    return {
        "price": round(price, 3),
        "year_usage": round(year_usage, 2),
    }


def get_oil_overall_stats(db: Session) -> OilOverallStats:
    total_volume = db.query(func.sum(OilDB.volume)).scalar() or 0
    total_costs = db.query(func.sum(OilDB.costs)).scalar() or 0
    number_of_years = (
        db.query(func.count(func.distinct(func.strftime("%Y", OilDB.date)))).scalar()
        or 1
    )
    average_volume = total_volume / number_of_years
    return OilOverallStats(
        total_volume=round(total_volume, 2),
        total_costs=round(total_costs, 2),
        number_of_years=number_of_years,
        average_volume=round(average_volume, 2),
    )


def get_oil_yearly_summary(db: Session) -> List[OilYearlySummary]:
    results = (
        db.query(
            func.strftime("%Y", OilDB.date).label("year"),
            func.sum(OilDB.volume).label("total_volume"),
            func.sum(OilDB.costs).label("total_costs"),
        )
        .group_by("year")
        .order_by("year")
        .all()
    )
    summary = []
    for r in results:
        summary.append(
            OilYearlySummary(
                year=int(r.year),
                total_volume=round(r.total_volume, 2),
                total_costs=round(r.total_costs, 2),
            )
        )
    return summary


def get_oil_price_trend(db: Session) -> List[OilPriceTrend]:
    results = (
        db.query(
            func.strftime("%Y", OilDB.date).label("year"),
            func.avg(OilDB.costs / OilDB.volume).label("average_price"),
        )
        .filter(OilDB.volume > 0)
        .group_by("year")
        .order_by("year")
        .all()
    )
    trends = []
    for r in results:
        trends.append(
            OilPriceTrend(year=int(r.year), average_price=round(r.average_price, 3))
        )
    return trends


def create_oil_fill_level_entry(db: Session, schema: OilFillLevelsCreate):
    return create_entry(db, OilFillLevelDB, schema)


def get_oil_fill_level_entries(db: Session):
    return get_entries(db, OilFillLevelDB)
