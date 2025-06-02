from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum

class ConfirmedBooking(Base):
    __tablename__ = "confirmed_bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, unique=True, index=True)
    contact_method = Column(String)
    language = Column(String)
    people_count = Column(Integer)
    date = Column(Date)
    total_price = Column(Float)
    pickup_location = Column(String)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    booking_type = Column(String)  # "excursion" или "car"
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=True)  # добавлено

    supplier = relationship("Supplier")

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    address = Column(String)
    supplier_type = Column(String)
    logo_url = Column(String)

    excursions = relationship("Excursion", back_populates="supplier")
    cars = relationship("Car", back_populates="supplier")

class Excursion(Base):
    __tablename__ = "excursions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description_en = Column(String)
    description_ru = Column(String)
    duration = Column(String)
    location_en = Column(String)
    location_ru = Column(String)
    price = Column(Float)
    adult_price = Column(Float)
    child_price = Column(Float)
    infant_price = Column(Float)
    image_urls = Column(String)
    operator_id = Column(Integer, ForeignKey("suppliers.id"))

    operator = relationship("Supplier", back_populates="excursions")

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String)
    model = Column(String)
    color = Column(String)
    seats = Column(Integer)
    price_per_day = Column(Float)
    image_url = Column(String)
    car_type = Column(String)
    transmission = Column(String)
    has_air_conditioning = Column(Boolean)

    year = Column(Integer)  # Год выпуска
    fuel_type = Column(String)  # бензин, газ, электричество
    engine_capacity = Column(Float)  # в литрах
    mileage = Column(Integer)  # пробег в км
    drive_type = Column(String)  # полный, передний, задний

    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    supplier = relationship("Supplier", back_populates="cars")

class CarReservation(Base):
    __tablename__ = "car_reservations"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"))
    start_date = Column(Date)
    end_date = Column(Date)

class ExcursionReservation(Base):
    __tablename__ = "excursion_reservations"

    id = Column(Integer, primary_key=True, index=True)
    excursion_id = Column(Integer, ForeignKey("excursions.id"))
    date = Column(Date)

class SupplierType(str, enum.Enum):
    tour = "tour"
    car = "car"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_superuser = Column(Boolean, default=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    current_token = Column(String, nullable=True)

    supplier = relationship("Supplier")