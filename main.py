from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from email_utils import send_booking_email
from database import SessionLocal
from models import ConfirmedBooking, TourOperator, Excursion, Car, CarReservation, ExcursionReservation
from datetime import datetime
from sqlalchemy.orm import Session

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class BookingData(BaseModel):
    first_name: str
    last_name: str
    phone: str
    contact_method: str
    email: str
    document_number: str
    language: str
    adults: int
    children: int
    infants: int
    excursion_title: str
    date: str  # ISO string
    total_price: float

@app.post("/api/pay")
def process_payment(booking: BookingData, db: Session = Depends(get_db)):
    # Имитация успешной оплаты
    payment_successful = True

    if not payment_successful:
        raise HTTPException(status_code=400, detail="Оплата не прошла")

    send_booking_email(booking)

    people_count = booking.adults + booking.children + booking.infants
    booking_id = int(datetime.utcnow().timestamp())

    booking_entry = ConfirmedBooking(
        booking_id=booking_id,
        contact_method=booking.contact_method,
        language=booking.language,
        people_count=people_count,
        date=datetime.strptime(booking.date, "%Y-%m-%d").date(),
        total_price=booking.total_price
    )
    db.add(booking_entry)
    db.commit()

    return {"status": "success", "booking_id": booking_id}

@app.get("/")
def root():
    return {"status": "Backend is running"}

@app.get("/bookings")
def get_bookings(db: Session = Depends(get_db)):
    bookings = db.query(ConfirmedBooking).order_by(ConfirmedBooking.id.desc()).all()
    return [
        {
            "booking_id": b.booking_id,
            "contact_method": b.contact_method,
            "language": b.language,
            "people_count": b.people_count,
            "date": b.date.isoformat(),
            "total_price": b.total_price
        }
        for b in bookings
    ]

@app.get("/operators")
def get_operators(db: Session = Depends(get_db)):
    operators = db.query(TourOperator).all()
    return [
        {
            "id": op.id,
            "name": op.name,
            "phone": op.phone,
            "email": op.email,
            "logo_url": op.logo_url
        }
        for op in operators
    ]

@app.get("/excursions")
def get_excursions(operator_id: int, db: Session = Depends(get_db)):
    excursions = db.query(Excursion).filter(Excursion.operator_id == operator_id).all()
    return [
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "duration": e.duration,
            "location": e.location,
            "price": e.price,
            "image_urls": e.image_urls,
            "operator_id": e.operator_id
        }
        for e in excursions
    ]

@app.get("/cars")
def get_cars(db: Session = Depends(get_db)):
    cars = db.query(Car).all()
    return [
        {
            "id": c.id,
            "brand": c.brand,
            "model": c.model,
            "seats": c.seats,
            "price_per_day": c.price_per_day,
            "image_url": c.image_url,
            "car_type": c.car_type,
            "transmission": c.transmission,
            "has_air_conditioning": c.has_air_conditioning
        }
        for c in cars
    ]
