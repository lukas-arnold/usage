from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db_oil
from app.schemas import (
    OilResponse,
    OilCreate,
    OilOverallStats,
    OilYearlySummary,
    OilPriceTrend,
)
from app.operations import oil

oil_router = APIRouter(prefix="/oil", tags=["Oil"])


oil_router.post(
    "/entries",
    response_model=OilResponse,
    status_code=status.HTTP_201_CREATED,
)


def create_oil_entry(entry: OilCreate, db: Session = Depends(get_db_oil)):
    db_entry = oil.create_oil_entry(db, entry)
    derived_fields = oil.calculate_oil_derived_fields(db_entry)
    return OilResponse(
        id=db_entry.id,
        date=db_entry.date,
        volume=db_entry.volume,
        costs=db_entry.costs,
        retailer=db_entry.retailer,
        note=db_entry.note,
        **derived_fields
    )


@oil_router.get("/entries", response_model=List[OilResponse])
def read_oil_entries(db: Session = Depends(get_db_oil)):
    entries = oil.get_oil_entries(db)
    response_entries = []
    for entry in entries:
        derived_fields = oil.calculate_oil_derived_fields(entry)
        response_entries.append(
            OilResponse(
                id=entry.id,
                date=entry.date,
                volume=entry.volume,
                costs=entry.costs,
                retailer=entry.retailer,
                note=entry.note,
                **derived_fields
            )
        )
    return response_entries


@oil_router.get("/entries/{entry_id}", response_model=OilResponse)
def read_oil_entry(entry_id: int, db: Session = Depends(get_db_oil)):
    db_entry = oil.get_oil_entry(db, entry_id)
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Oil entry not found")
    derived_fields = oil.calculate_oil_derived_fields(db_entry)
    return OilResponse(
        id=db_entry.id,
        date=db_entry.date,
        volume=db_entry.volume,
        costs=db_entry.costs,
        retailer=db_entry.retailer,
        note=db_entry.note,
        **derived_fields
    )


@oil_router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_oil_entry(entry_id: int, db: Session = Depends(get_db_oil)):
    if not oil.delete_oil_entry(db, entry_id):
        raise HTTPException(status_code=404, detail="Oil entry not found")
    return {"ok": True}


@oil_router.get("/stats/overall", response_model=OilOverallStats)
def get_oil_overall_stats(db: Session = Depends(get_db_oil)):
    return oil.get_oil_overall_stats(db)


@oil_router.get("/stats/yearly_summary", response_model=List[OilYearlySummary])
def get_oil_yearly_summary(db: Session = Depends(get_db_oil)):
    return oil.get_oil_yearly_summary(db)


@oil_router.get("/stats/price_trend", response_model=List[OilPriceTrend])
def get_oil_price_trend(db: Session = Depends(get_db_oil)):
    return oil.get_oil_price_trend(db)
