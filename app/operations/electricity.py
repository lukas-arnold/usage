from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Optional
from datetime import date, timedelta

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


# --- Helper function to calculate days ---
def get_days_in_period(time_from: date, time_to: date) -> int:
    """Calculates the number of days between two dates (inclusive of time_from, exclusive of time_to)."""
    return (time_to - time_from).days


def get_electricity_overall_stats(db: Session) -> ElectricityOverallStats:
    """
    Calculates overall electricity statistics, accounting for partial years.
    Sums total usage and costs, determines the overall time span in years (float),
    and calculates average yearly usage and costs based on this span.
    """
    # Fetch all relevant data for processing in Python.
    # For very large datasets, consider performing these calculations directly in SQL.
    all_electricity_data = db.query(
        ElectricityDB.time_from,
        ElectricityDB.time_to,
        ElectricityDB.usage,
        ElectricityDB.costs,
    ).all()

    total_usage = 0.0
    total_costs = 0.0
    min_date: Optional[date] = None
    max_date: Optional[date] = None

    for entry_time_from, entry_time_to, usage, costs in all_electricity_data:
        duration_days = get_days_in_period(entry_time_from, entry_time_to)

        # Skip entries with invalid or zero duration
        if duration_days <= 0:
            continue

        total_usage += usage
        total_costs += costs

        # Track the overall span of data
        if min_date is None or entry_time_from < min_date:
            min_date = entry_time_from
        if max_date is None or entry_time_to > max_date:
            max_date = entry_time_to

    if min_date is None or max_date is None:
        # No data available
        return ElectricityOverallStats(
            total_usage=0.0,
            total_costs=0.0,
            number_of_years=0.0,
            average_yearly_usage=0.0,
        )

    # Calculate total duration of covered data in days
    total_span_days = (max_date - min_date).days

    # Convert total days to years (float) for accurate averaging, considering leap years
    number_of_years = total_span_days / 365.25 if total_span_days > 0 else 0.0

    # Calculate yearly average
    average_yearly_usage = (
        (total_usage / number_of_years) if number_of_years > 0 else 0.0
    )

    return ElectricityOverallStats(
        total_usage=round(total_usage, 2),
        total_costs=round(total_costs, 2),
        number_of_years=round(number_of_years, 2),
        average_yearly_usage=round(average_yearly_usage, 2),
    )


def get_electricity_yearly_summary(
    db: Session,
) -> List[ElectricityYearlySummary]:
    """
    Generates a yearly summary of electricity usage and costs.
    It splits usage and costs of entries that span across year boundaries
    proportionally to the days covered within each respective year.
    """
    # Fetch all data for processing
    all_electricity_data = db.query(
        ElectricityDB.time_from,
        ElectricityDB.time_to,
        ElectricityDB.usage,
        ElectricityDB.costs,
    ).all()

    # Dictionary to store aggregated data per year: {year: {'total_usage': float, 'total_costs': float, 'total_days': int}}
    yearly_data = {}

    for entry_time_from, entry_time_to, usage, costs in all_electricity_data:
        duration_days = get_days_in_period(entry_time_from, entry_time_to)
        if duration_days <= 0:  # Skip invalid periods
            continue

        # Calculate daily rates for proportional distribution
        daily_usage_rate = usage / duration_days
        daily_costs_rate = costs / duration_days

        current_date = entry_time_from
        while current_date < entry_time_to:
            year = current_date.year

            # Determine the end of the current segment for this year
            end_of_year = date(year, 12, 31)
            # The actual end of the period for this year, considering the entry's end date
            segment_end = min(entry_time_to, end_of_year + timedelta(days=1))

            # Days within the current year segment for this specific entry
            days_in_current_year_for_entry = (segment_end - current_date).days

            # Initialize year data if not present
            if year not in yearly_data:
                yearly_data[year] = {
                    "total_usage": 0.0,
                    "total_costs": 0.0,
                    "total_days": 0,
                }

            # Add weighted values to the corresponding year
            yearly_data[year]["total_usage"] += (
                daily_usage_rate * days_in_current_year_for_entry
            )
            yearly_data[year]["total_costs"] += (
                daily_costs_rate * days_in_current_year_for_entry
            )
            yearly_data[year]["total_days"] += days_in_current_year_for_entry

            # Move to the next day, ensuring we don't exceed the entry's end date
            current_date = segment_end

    summary = []
    # Sort years for consistent output
    for year in sorted(yearly_data.keys()):
        data = yearly_data[year]
        summary.append(
            ElectricityYearlySummary(
                year=year,
                total_usage=round(data["total_usage"], 2),
                total_costs=round(data["total_costs"], 2),
            )
        )
    return summary


def get_electricity_price_trend(db: Session) -> List[ElectricityPriceTrend]:
    results = (
        db.query(
            func.strftime("%Y", ElectricityDB.time_from).label("year"),
            func.avg(ElectricityDB.costs / ElectricityDB.usage).label("average_price"),
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
                year=int(r.year), average_price=round(r.average_price, 3)
            )
        )
    return trends
