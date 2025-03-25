import smtplib
from email.mime.text import MIMEText

def send_booking_email(booking):
    msg = MIMEText(f"""
Новая заявка на экскурсию:

Экскурсия: {booking.excursion_title}
Дата: {booking.date}
Имя: {booking.first_name} {booking.last_name}
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
    msg['Subject'] = f"Бронирование: {booking.excursion_title} ({booking.date})"
    msg['From'] = "your@email.com"
    msg['To'] = "operator@email.com"

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login("your@email.com", "your_app_password")
        server.send_message(msg)
