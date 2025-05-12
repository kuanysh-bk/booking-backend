import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные из .env


def send_booking_email(booking):
    msg = MIMEText(f"""
Новая заявка на экскурсию:

Экскурсия: {booking.excursion_title}
Дата: {booking.date}
Имя: {booking.firstName} {booking.lastName}
Телефон: {booking.phone}
Email: {booking.email}
Документ: {booking.document_number}
Метод связи: {booking.contact_method}
Язык: {booking.language}

Участники:
Взрослых: {booking.adults}
Детей: {booking.children}
Младенцев: {booking.infants}

Итого: {booking.total_price} AED
""")

    from_email = os.getenv("EMAIL_USER")
    to_email = os.getenv("EMAIL_TO")
    password = os.getenv("EMAIL_PASS")

    msg['Subject'] = f"Бронирование: {booking.excursion_title} ({booking.date})"
    msg['From'] = from_email
    msg['To'] = to_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(from_email, password)
        server.send_message(msg)