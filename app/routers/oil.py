from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, crud
from ..database import get_db_oil

oil_router = APIRouter(prefix="/api/oil", tags=["Oil"])


@oil_router.post(
    "/entries", response_model=schemas.OilResponse, status_code=status.HTTP_201_CREATED
)
def create_oil_entry(entry: schemas.OilCreate, db: Session = Depends(get_db_oil)):
    db_entry = crud.create_entry(db, models.OilDB, entry)
    derived_fields = crud.calculate_oil_derived_fields(db, db_entry)
    return schemas.OilResponse(**db_entry.__dict__, **derived_fields)


@oil_router.get("/entries", response_model=List[schemas.OilResponse])
def read_oil_entries(db: Session = Depends(get_db_oil)):
    entries = crud.get_entries(db, models.OilDB)
    response_entries = []
    for entry in entries:
        derived_fields = crud.calculate_oil_derived_fields(db, entry)
        response_entries.append(schemas.OilResponse(**entry.__dict__, **derived_fields))
    return response_entries


@oil_router.get("/entries/{entry_id}", response_model=schemas.OilResponse)
def read_oil_entry(entry_id: int, db: Session = Depends(get_db_oil)):
    db_entry = crud.get_entry(db, models.OilDB, entry_id)
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Oil entry not found")
    derived_fields = crud.calculate_oil_derived_fields(db, db_entry)
    return schemas.OilResponse(**db_entry.__dict__, **derived_fields)


@oil_router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_oil_entry(entry_id: int, db: Session = Depends(get_db_oil)):
    if not crud.delete_entry(db, models.OilDB, entry_id):
        raise HTTPException(status_code=404, detail="Oil entry not found")
    return {"ok": True}


@oil_router.get("/stats/overall", response_model=schemas.OilOverallStats)
def get_oil_overall_stats(db: Session = Depends(get_db_oil)):
    return crud.get_oil_overall_stats(db)


@oil_router.get("/stats/price_trend", response_model=List[schemas.OilPriceTrend])
def get_oil_price_trend(db: Session = Depends(get_db_oil)):
    return crud.get_oil_price_trend(db)
