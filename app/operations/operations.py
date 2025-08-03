from typing import Type, TypeVar, List, Union, Optional
from sqlalchemy.orm import Session
from app import models, schemas


ModelType = TypeVar("ModelType", bound=models.BaseModelMixin)


def create_entry(
    db: Session,
    model: Type[ModelType],
    entry_schema: Union[
        schemas.ElectricityCreate,
        schemas.OilCreate,
        schemas.OilFillLevelsCreate,
        schemas.WaterCreate,
    ],
) -> ModelType:
    db_entry = model(**entry_schema.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def get_entry(
    db: Session, model: Type[ModelType], entry_id: int
) -> Optional[ModelType]:
    return db.query(model).filter(model.id == entry_id).first()


def get_entries(db: Session, model: Type[ModelType]) -> List[ModelType]:
    return db.query(model).all()


def delete_entry(db: Session, model: Type[ModelType], entry_id: int) -> bool:
    db_entry = db.query(model).filter(model.id == entry_id).first()
    if db_entry:
        db.delete(db_entry)
        db.commit()
        return True
    return False


def calculate_price(costs: float, usage: float) -> float:
    return costs / usage if usage else 0.0


def calculate_monthly_payment(payments: float) -> float:
    return payments / 12 if payments else 0.0


def calculate_monthly_payment_dynamic(payments: float, days: int) -> float:
    if days <= 0:
        return 0.0
    average_daily_payment = payments / days
    return average_daily_payment * 30.44  # average month


def calculate_difference(costs: float, payments: float) -> float:
    return costs - payments
