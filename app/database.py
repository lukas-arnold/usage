from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_ELECTRICITY_DATABASE_URL = "sqlite:///./electricity.db"
SQLALCHEMY_OIL_DATABASE_URL = "sqlite:///./oil.db"
SQLALCHEMY_WATER_DATABASE_URL = "sqlite:///./water.db"

engine_electricity = create_engine(
    SQLALCHEMY_ELECTRICITY_DATABASE_URL, connect_args={"check_same_thread": False}
)
engine_oil = create_engine(
    SQLALCHEMY_OIL_DATABASE_URL, connect_args={"check_same_thread": False}
)
engine_water = create_engine(
    SQLALCHEMY_WATER_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocalElectricity = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_electricity
)
SessionLocalOil = sessionmaker(autocommit=False, autoflush=False, bind=engine_oil)
SessionLocalWater = sessionmaker(autocommit=False, autoflush=False, bind=engine_water)

Base = declarative_base()


def init_db():
    Base.metadata.create_all(bind=engine_electricity)
    Base.metadata.create_all(bind=engine_oil)
    Base.metadata.create_all(bind=engine_water)


def get_db_electricity():
    db = SessionLocalElectricity()
    try:
        yield db
    finally:
        db.close()


def get_db_oil():
    db = SessionLocalOil()
    try:
        yield db
    finally:
        db.close()


def get_db_water():
    db = SessionLocalWater()
    try:
        yield db
    finally:
        db.close()
