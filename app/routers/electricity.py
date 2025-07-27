from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, crud
from ..database import get_db_electricity

electricity_router = APIRouter(prefix="/api/electricity", tags=["Electricity"])


@electricity_router.post(
    "/entries",
    response_model=schemas.ElectricityResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_electricity_entry(
    entry: schemas.ElectricityCreate, db: Session = Depends(get_db_electricity)
):
    db_entry = crud.create_entry(db, models.ElectricityDB, entry)
    derived_fields = crud.calculate_electricity_derived_fields(db_entry)
    return schemas.ElectricityResponse(**db_entry.__dict__, **derived_fields)


@electricity_router.get("/entries", response_model=List[schemas.ElectricityResponse])
def read_electricity_entries(db: Session = Depends(get_db_electricity)):
    entries = crud.get_entries(db, models.ElectricityDB)
    response_entries = []
    for entry in entries:
        derived_fields = crud.calculate_electricity_derived_fields(entry)
        response_entries.append(
            schemas.ElectricityResponse(**entry.__dict__, **derived_fields)
        )
    return response_entries


@electricity_router.get(
    "/entries/{entry_id}", response_model=schemas.ElectricityResponse
)
def read_electricity_entry(entry_id: int, db: Session = Depends(get_db_electricity)):
    db_entry = crud.get_entry(db, models.ElectricityDB, entry_id)
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Electricity entry not found")
    derived_fields = crud.calculate_electricity_derived_fields(db_entry)
    return schemas.ElectricityResponse(**db_entry.__dict__, **derived_fields)


@electricity_router.delete(
    "/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_electricity_entry(entry_id: int, db: Session = Depends(get_db_electricity)):
    if not crud.delete_entry(db, models.ElectricityDB, entry_id):
        raise HTTPException(status_code=404, detail="Electricity entry not found")
    return {"ok": True}


@electricity_router.get(
    "/stats/overall", response_model=schemas.ElectricityOverallStats
)
def get_electricity_overall_stats(db: Session = Depends(get_db_electricity)):
    return crud.get_electricity_overall_stats(db)


@electricity_router.get(
    "/stats/price_trend", response_model=List[schemas.ElectricityPriceTrend]
)
def get_electricity_price_trend(db: Session = Depends(get_db_electricity)):
    return crud.get_electricity_price_trend(db)
