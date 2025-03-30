from database import SessionLocal
from models import TourOperator, Excursion, Car

# Открываем сессию
session = SessionLocal()

# Туроператоры
tour_operators = [
    TourOperator(name="Dubai Adventures", phone="+971-50-123-4567", email="info@dubaiadv.com", logo_url="https://example.com/logo1.png"),
    TourOperator(name="Emirates Tours", phone="+971-55-765-4321", email="contact@emiratestours.com", logo_url="https://example.com/logo2.png")
]
session.add_all(tour_operators)
session.commit()

# Экскурсии
excursions = [
    Excursion(
        title="City Tour Dubai",
        description="Обзорная экскурсия по Дубаю с русским гидом.",
        duration="4 часа",
        location="Дубай",
        price=200,
        image_urls="https://example.com/dubai1.jpg,https://example.com/dubai2.jpg",
        operator_id=tour_operators[0].id
    ),
    Excursion(
        title="Safari Desert",
        description="Сафари по пустыне с ужином.",
        duration="6 часов",
        location="Пустыня",
        price=350,
        image_urls="https://example.com/safari1.jpg,https://example.com/safari2.jpg",
        operator_id=tour_operators[1].id
    )
]
session.add_all(excursions)
session.commit()

# Машины
cars = [
    Car(
        brand="Toyota",
        model="Camry",
        color="Белый",
        seats=5,
        price_per_day=150,
        image_url="https://example.com/camry.jpg",
        car_type="Седан",
        transmission="Автомат",
        has_air_conditioning=True
    ),
    Car(
        brand="Nissan",
        model="Patrol",
        color="Черный",
        seats=7,
        price_per_day=350,
        image_url="https://example.com/patrol.jpg",
        car_type="Джип",
        transmission="Автомат",
        has_air_conditioning=True
    )
]
session.add_all(cars)
session.commit()

session.close()
print("✅ Данные успешно добавлены в базу")