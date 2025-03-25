from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from email_utils import send_booking_email

app = FastAPI()

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
    date: str
    total_price: float

@app.post("/api/pay")
def process_payment(booking: BookingData):
    # Эмуляция успешной оплаты (заменить на реальную POS-интеграцию)
    payment_successful = True

    if not payment_successful:
        raise HTTPException(status_code=400, detail="Платеж не прошел")

    send_booking_email(booking)
    return { "status": "success" }
