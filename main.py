from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from database import SessionLocal, engine
from models import ConfirmedBooking, Supplier, Excursion, Car, CarReservation, ExcursionReservation
from datetime import datetime, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://kuks-booking.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from models import Base
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class BookingData(BaseModel):
    firstName: str
    lastName: str
    phone: str
    contact_method: str
    email: str | None = None
    document_number: str | None = None
    language: str | None = None
    adults: int | None = None
    children: int | None = None
    infants: int | None = None
    excursion_title: str | None = None
    date: str
    start_date: str | None = None
    end_date: str | None = None
    total_price: float
    pickup_location: str | None = None
    supplier_id: int
    booking_type: str  # "excursion" или "car"
    car_id: int | None = None  # добавлено


@app.post("/api/pay")
def process_payment(booking: BookingData, db: Session = Depends(get_db)):
    booking_id = int(datetime.utcnow().timestamp())

    total_people = booking.adults + booking.children + booking.infants if booking.booking_type == "excursion" else 1
    date_obj = datetime.strptime(booking.date, "%Y-%m-%d").date() if booking.date else None
    date_from_obj = datetime.strptime(booking.start_date, "%Y-%m-%d").date() if booking.start_date else None
    date_to_obj = datetime.strptime(booking.end_date, "%Y-%m-%d").date() if booking.end_date else None

    booking_entry = ConfirmedBooking(
        booking_id=booking_id,
        contact_method=booking.contact_method,
        language=booking.language,
        people_count=total_people,
        date=date_obj or date_from_obj,
        total_price=booking.total_price or 0,
        pickup_location=booking.pickup_location,
        supplier_id=booking.supplier_id,
        booking_type=booking.booking_type,
        car_id=booking.car_id  # добавлено
    )
    db.add(booking_entry)
    db.commit()
    db.refresh(booking_entry)

     # ➕ если бронируется машина — записываем диапазон в cars_reservation
    if booking.booking_type == "car" and booking.car_id:
        res = CarReservation(
            car_id=booking.car_id,
            start_date=date_from_obj,
            end_date=date_to_obj
        )
        db.add(res)
        db.commit()

    from email_utils import send_booking_email  # импорт функции (если в отдельном файле)
    send_booking_email(booking)

    return {"status": "success", "booking_id": booking_entry.booking_id}

@app.get("/operators")
def get_operators(db: Session = Depends(get_db)):
    return db.query(Supplier).all()

@app.get("/excursions")
def get_excursions(operator_id: int, db: Session = Depends(get_db)):
    return db.query(Excursion).filter(Excursion.operator_id == operator_id).all()

@app.get("/cars")
def get_cars(db: Session = Depends(get_db)):
    cars = db.query(Car).options(joinedload(Car.supplier)).all()
    result = []
    for car in cars:
        result.append({
            "id": car.id,
            "brand": car.brand,
            "model": car.model,
            "color": car.color,
            "seats": car.seats,
            "price_per_day": car.price_per_day,
            "image_url": car.image_url,
            "car_type": car.car_type,
            "transmission": car.transmission,
            "has_air_conditioning": car.has_air_conditioning,
            "year": car.year,
            "fuel_type": car.fuel_type,
            "engine_capacity": car.engine_capacity,
            "mileage": car.mileage,
            "drive_type": car.drive_type,
            "supplier": {
                "id": car.supplier.id,
                "name": car.supplier.name
            } if car.supplier else None
        })
    return result

@app.get("/bookings")
def get_bookings(db: Session = Depends(get_db)):
    return db.query(ConfirmedBooking).all()

@app.get("/excursion-reservations")
def get_excursion_reservations(excursion_id: int, db: Session = Depends(get_db)):
    return db.query(ExcursionReservation).filter(ExcursionReservation.excursion_id == excursion_id).all()

@app.get("/car-reservations")
def get_car_reservations(car_id: int, db: Session = Depends(get_db)):
    reservations = db.query(CarReservation).filter(CarReservation.car_id == car_id).all()
    dates = []

    for r in reservations:
        current = r.start_date
        while current <= r.end_date:
            dates.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)

    return dates

@app.get("/cars/{car_id}")
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(Car).options(joinedload(Car.supplier)).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return {
        "id": car.id,
        "brand": car.brand,
        "model": car.model,
        "price_per_day": car.price_per_day,
        "supplier_id": car.supplier_id,
        "supplier": {"id": car.supplier.id, "name": car.supplier.name} if car.supplier else None
    }