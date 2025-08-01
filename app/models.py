from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date as date_


class BaseElectricity(DeclarativeBase):
    pass


class BaseOil(DeclarativeBase):
    pass


class BaseWater(DeclarativeBase):
    pass


class BaseModelMixin:
    id: Mapped[int] = mapped_column(primary_key=True, index=True)


class ElectricityDB(BaseElectricity, BaseModelMixin):
    __tablename__ = "electricity"

    time_from: Mapped[date_] = mapped_column(nullable=False)
    time_to: Mapped[date_] = mapped_column(nullable=False)
    usage: Mapped[int] = mapped_column(nullable=False)
    costs: Mapped[float] = mapped_column(nullable=False)
    retailer: Mapped[str] = mapped_column(nullable=False)
    payments: Mapped[float] = mapped_column(nullable=False)
    note: Mapped[str | None] = mapped_column(nullable=True)


class OilDB(BaseOil, BaseModelMixin):
    __tablename__ = "oil"

    date: Mapped[date_] = mapped_column(nullable=False)
    volume: Mapped[int] = mapped_column(nullable=False)
    costs: Mapped[float] = mapped_column(nullable=False)
    retailer: Mapped[str] = mapped_column(nullable=False)
    note: Mapped[str | None] = mapped_column(nullable=True)


class OilFillLevelDB(BaseOil, BaseModelMixin):
    __tablename__ = "oil_fill_level"

    date: Mapped[date_] = mapped_column(nullable=False)
    level: Mapped[float] = mapped_column(nullable=False)


class WaterDB(BaseWater, BaseModelMixin):
    __tablename__ = "water"

    year: Mapped[int] = mapped_column(nullable=False)
    volume_water: Mapped[int] = mapped_column(nullable=False)
    volume_wastewater: Mapped[int] = mapped_column(nullable=False)
    volume_rainwater: Mapped[int] = mapped_column(nullable=False)
    costs_water: Mapped[float] = mapped_column(nullable=False)
    costs_wastewater: Mapped[float] = mapped_column(nullable=False)
    costs_rainwater: Mapped[float] = mapped_column(nullable=False)
    payments: Mapped[float] = mapped_column(nullable=False)
    fixed_price: Mapped[float] = mapped_column(nullable=False)
    note: Mapped[str | None] = mapped_column(nullable=True)
