from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import ConfirmedBooking, TourOperator, Excursion, Car
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
    document_number: str
    language: str
    adults: int
    children: int
    infants: int
    excursion_title: str
    date: str
    total_price: float
    pickup_location: str | None = None

@app.post("/api/pay")
def process_payment(booking: BookingData, db: Session = Depends(get_db)):
    booking_entry = ConfirmedBooking(
        booking_id=int(datetime.utcnow().timestamp()),
        contact_method=booking.contact_method,
        language=booking.language,
        people_count=booking.adults + booking.children + booking.infants,
        date=datetime.strptime(booking.date, "%Y-%m-%d").date(),
        total_price=booking.total_price,
        pickup_location=booking.pickup_location
    )
    db.add(booking_entry)
    db.commit()
    db.refresh(booking_entry)

    from email_utils import send_booking_email  # импорт функции (если в отдельном файле)
    send_booking_email(booking)

    return {"status": "success", "booking_id": booking_entry.booking_id}

@app.get("/operators")
def get_operators(db: Session = Depends(get_db)):
    return db.query(TourOperator).all()

@app.get("/excursions")
def get_excursions(operator_id: int, db: Session = Depends(get_db)):
    return db.query(Excursion).filter(Excursion.operator_id == operator_id).all()

@app.get("/cars")
def get_cars(db: Session = Depends(get_db)):
    return db.query(Car).all()

@app.get("/bookings")
def get_bookings(db: Session = Depends(get_db)):
    return db.query(ConfirmedBooking).all()
