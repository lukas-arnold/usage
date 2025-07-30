from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db_water
from app.schemas import (
    WaterResponse,
    WaterCreate,
    WaterOverallStats,
    WaterYearlySummary,
    WaterPriceTrend,
)
from app.operations import water


water_router = APIRouter(prefix="/water", tags=["Water"])


@water_router.post(
    "/entries",
    response_model=WaterResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_water_entry(entry: WaterCreate, db: Session = Depends(get_db_water)):
    db_entry = water.create_water_entry(db, entry)
    derived_fields = water.calculate_water_derived_fields(db_entry)
    return WaterResponse(
        id=db_entry.id,
        year=db_entry.year,
        volume_water=db_entry.volume_water,
        volume_wastewater=db_entry.volume_wastewater,
        volume_rainwater=db_entry.volume_rainwater,
        costs_water=db_entry.costs_water,
        costs_wastewater=db_entry.costs_wastewater,
        costs_rainwater=db_entry.costs_rainwater,
        payments=db_entry.payments,
        fixed_price=db_entry.fixed_price,
        note=db_entry.note,
        **derived_fields
    )


@water_router.get("/entries", response_model=List[WaterResponse])
def read_water_entries(db: Session = Depends(get_db_water)):
    entries = water.get_water_entries(db)
    response_entries = []
    for entry in entries:
        derived_fields = water.calculate_water_derived_fields(entry)
        response_entries.append(
            WaterResponse(
                id=entry.id,
                year=entry.year,
                volume_water=entry.volume_water,
                volume_wastewater=entry.volume_wastewater,
                volume_rainwater=entry.volume_rainwater,
                costs_water=entry.costs_water,
                costs_wastewater=entry.costs_wastewater,
                costs_rainwater=entry.costs_rainwater,
                payments=entry.payments,
                fixed_price=entry.fixed_price,
                note=entry.note,
                **derived_fields
            )
        )
    response_entries.sort(key=lambda x: x.year, reverse=True)
    return response_entries


@water_router.get("/entries/{entry_id}", response_model=WaterResponse)
def read_water_entry(entry_id: int, db: Session = Depends(get_db_water)):
    db_entry = water.get_water_entry(db, entry_id)
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Water entry not found")
    derived_fields = water.calculate_water_derived_fields(db_entry)
    return WaterResponse(
        id=db_entry.id,
        year=db_entry.year,
        volume_water=db_entry.volume_water,
        volume_wastewater=db_entry.volume_wastewater,
        volume_rainwater=db_entry.volume_rainwater,
        costs_water=db_entry.costs_water,
        costs_wastewater=db_entry.costs_wastewater,
        costs_rainwater=db_entry.costs_rainwater,
        payments=db_entry.payments,
        fixed_price=db_entry.fixed_price,
        note=db_entry.note,
        **derived_fields
    )


@water_router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_water_entry(entry_id: int, db: Session = Depends(get_db_water)):
    if not water.delete_water_entry(db, entry_id):
        raise HTTPException(status_code=404, detail="Water entry not found")
    return {"ok": True}


@water_router.get("/stats/overall", response_model=WaterOverallStats)
def get_water_overall_stats(db: Session = Depends(get_db_water)):
    return water.get_water_overall_stats(db)


@water_router.get("/stats/yearly_summary", response_model=List[WaterYearlySummary])
def get_water_yearly_summary(db: Session = Depends(get_db_water)):
    return water.get_water_yearly_summary(db)


@water_router.get("/stats/price_trend", response_model=List[WaterPriceTrend])
def get_water_price_trend(db: Session = Depends(get_db_water)):
    return water.get_water_price_trend(db)
