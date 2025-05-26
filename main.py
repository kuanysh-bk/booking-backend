from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import ConfirmedBooking, Supplier, Excursion, Car, CarReservation, ExcursionReservation
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    language: str
    adults: int
    children: int
    infants: int
    excursion_title: str | None = None
    date: str
    total_price: float
    pickup_location: str | None = None
    supplier_id: int
    booking_type: str  # "excursion" или "car"
    car_id: int | None = None  # добавлено


@app.post("/api/pay")
def process_payment(booking: BookingData, db: Session = Depends(get_db)):
    print(">>> Получен payload:")
    print(booking.dict())
    booking_entry = ConfirmedBooking(
        booking_id=int(datetime.utcnow().timestamp()),
        contact_method=booking.contact_method,
        language=booking.language,
        people_count=booking.adults + booking.children + booking.infants,
        date=datetime.strptime(booking.date, "%Y-%m-%d").date(),
        total_price=booking.total_price,
        pickup_location=booking.pickup_location,
        supplier_id=booking.supplier_id,
        booking_type=booking.booking_type,
        car_id=booking.car_id  # добавлено
    )
    db.add(booking_entry)
    db.commit()
    db.refresh(booking_entry)

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
    return db.query(Car).all()

@app.get("/bookings")
def get_bookings(db: Session = Depends(get_db)):
    return db.query(ConfirmedBooking).all()

@app.get("/excursion-reservations")
def get_excursion_reservations(excursion_id: int, db: Session = Depends(get_db)):
    return db.query(ExcursionReservation).filter(ExcursionReservation.excursion_id == excursion_id).all()