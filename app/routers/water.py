from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, crud
from ..database import get_db_water

water_router = APIRouter(prefix="/api/water", tags=["Water"])


@water_router.post(
    "/entries",
    response_model=schemas.WaterResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_water_entry(entry: schemas.WaterCreate, db: Session = Depends(get_db_water)):
    db_entry = crud.create_entry(db, models.WaterDB, entry)
    derived_fields = crud.calculate_water_derived_fields(db_entry)
    return schemas.WaterResponse(**db_entry.__dict__, **derived_fields)


@water_router.get("/entries", response_model=List[schemas.WaterResponse])
def read_water_entries(db: Session = Depends(get_db_water)):
    entries = crud.get_entries(db, models.WaterDB)
    response_entries = []
    for entry in entries:
        derived_fields = crud.calculate_water_derived_fields(entry)
        response_entries.append(
            schemas.WaterResponse(**entry.__dict__, **derived_fields)
        )
    return response_entries


@water_router.get("/entries/{entry_id}", response_model=schemas.WaterResponse)
def read_water_entry(entry_id: int, db: Session = Depends(get_db_water)):
    db_entry = crud.get_entry(db, models.WaterDB, entry_id)
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Water entry not found")
    derived_fields = crud.calculate_water_derived_fields(db_entry)
    return schemas.WaterResponse(**db_entry.__dict__, **derived_fields)


@water_router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_water_entry(entry_id: int, db: Session = Depends(get_db_water)):
    if not crud.delete_entry(db, models.WaterDB, entry_id):
        raise HTTPException(status_code=404, detail="Water entry not found")
    return {"ok": True}


@water_router.get("/stats/overall", response_model=schemas.WaterOverallStats)
def get_water_overall_stats(db: Session = Depends(get_db_water)):
    return crud.get_water_overall_stats(db)


@water_router.get("/stats/price_trend", response_model=List[schemas.WaterPriceTrend])
def get_water_price_trend(db: Session = Depends(get_db_water)):
    return crud.get_water_price_trend(db)
