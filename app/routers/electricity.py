from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db_electricity
from app.schemas import (
    ElectricityResponse,
    ElectricityCreate,
    ElectricityOverallStats,
    ElectricityYearlySummary,
    ElectricityPriceTrend,
)
from app.operations import electricity

electricity_router = APIRouter(prefix="/electricity", tags=["Electricity"])


@electricity_router.post(
    "/entries",
    response_model=ElectricityResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_electricity_entry(
    entry: ElectricityCreate, db: Session = Depends(get_db_electricity)
):
    db_entry = electricity.create_electricity_entry(db, entry)
    derived_fields = electricity.calculate_electricity_derived_fields(db_entry)
    return ElectricityResponse(
        id=db_entry.id,
        time_from=db_entry.time_from,
        time_to=db_entry.time_to,
        usage=db_entry.usage,
        costs=db_entry.costs,
        retailer=db_entry.retailer,
        payments=db_entry.payments,
        note=db_entry.note,
        **derived_fields,
    )


@electricity_router.get("/entries", response_model=List[ElectricityResponse])
def read_electricity_entries(db: Session = Depends(get_db_electricity)):
    entries = electricity.get_electricity_entries(db)
    response_entries = []
    for entry in entries:
        derived_fields = electricity.calculate_electricity_derived_fields(entry)
        response_entries.append(
            ElectricityResponse(
                id=entry.id,
                time_from=entry.time_from,
                time_to=entry.time_to,
                usage=entry.usage,
                costs=entry.costs,
                retailer=entry.retailer,
                payments=entry.payments,
                note=entry.note,
                **derived_fields,
            )
        )
    response_entries.sort(key=lambda x: x.time_from, reverse=True)
    return response_entries


@electricity_router.get("/entries/{entry_id}", response_model=ElectricityResponse)
def read_electricity_entry(entry_id: int, db: Session = Depends(get_db_electricity)):
    db_entry = electricity.get_electricity_entry(db, entry_id)
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Electricity entry not found")
    derived_fields = electricity.calculate_electricity_derived_fields(db_entry)
    return ElectricityResponse(
        id=db_entry.id,
        time_from=db_entry.time_from,
        time_to=db_entry.time_to,
        usage=db_entry.usage,
        costs=db_entry.costs,
        retailer=db_entry.retailer,
        payments=db_entry.payments,
        note=db_entry.note,
        **derived_fields,
    )


@electricity_router.delete(
    "/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_electricity_entry(entry_id: int, db: Session = Depends(get_db_electricity)):
    if not electricity.delete_electricity_entry(db, entry_id):
        raise HTTPException(status_code=404, detail="Electricity entry not found")
    return {"ok": True}


@electricity_router.get("/stats/overall", response_model=ElectricityOverallStats)
def get_electricity_overall_stats(db: Session = Depends(get_db_electricity)):
    return electricity.get_electricity_overall_stats(db)


@electricity_router.get(
    "/stats/yearly_summary", response_model=List[ElectricityYearlySummary]
)
def get_electricity_yearly_summary_data(db: Session = Depends(get_db_electricity)):
    return electricity.get_electricity_yearly_summary(db)


@electricity_router.get(
    "/stats/price_trend", response_model=List[ElectricityPriceTrend]
)
def get_electricity_price_trend(db: Session = Depends(get_db_electricity)):
    return electricity.get_electricity_price_trend(db)
