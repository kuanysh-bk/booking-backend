from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Автоматическое создание таблиц при запуске
from models import ConfirmedBooking, TourOperator, Excursion, Car, CarReservation, ExcursionReservation
Base.metadata.create_all(bind=engine)