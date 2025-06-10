import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные из .env


def send_booking_email(booking):
    if booking.booking_type == "excursion":
        body = f"""
Новая заявка на экскурсию:

Экскурсия: {booking.excursion_title}
Дата: {booking.date}
Имя: {booking.firstName} {booking.lastName}
Телефон: {booking.phone}
Email: {booking.email}
Документ: {booking.document_number}
Место встречи: {booking.pickup_location}
Метод связи: {booking.contact_method}
Язык: {booking.language}

Участники:
Взрослых: {booking.adults}
Детей: {booking.children}
Младенцев: {booking.infants}

Итого: {booking.total_price} AED
"""
        subject = f"Бронирование: {booking.excursion_title} ({booking.date})"
    else:
        body = f"""
Новая заявка на аренду авто:

Имя: {booking.firstName} {booking.lastName}
Телефон: {booking.phone}
Email: {booking.email}
Документ: {booking.document_number}
Метод связи: {booking.contact_method}
Дата начала: {booking.start_date}
Дата окончания: {booking.end_date}

Итого: {booking.total_price} AED
"""
        subject = f"Аренда авто: {booking.firstName} {booking.lastName} ({booking.start_date})"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = os.getenv("EMAIL_TO")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(msg['From'], os.getenv("EMAIL_PASS"))
        server.send_message(msg)