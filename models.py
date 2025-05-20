from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base

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

class TourOperator(Base):
    __tablename__ = "tour_operators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String)
    email = Column(String)
    logo_url = Column(String)

    excursions = relationship("Excursion", back_populates="operator")

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
    operator_id = Column(Integer, ForeignKey("tour_operators.id"))

    operator = relationship("TourOperator", back_populates="excursions")

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String)
    model = Column(String)
    color = Column(String)  # новый параметр
    seats = Column(Integer)
    price_per_day = Column(Float)
    image_url = Column(String)
    car_type = Column(String)
    transmission = Column(String)
    has_air_conditioning = Column(Boolean)

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