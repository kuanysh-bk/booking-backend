from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from database import SessionLocal, engine, get_db
from models import ConfirmedBooking, Supplier, Excursion, Car, CarReservation, ExcursionReservation, User, Base
from datetime import datetime, timedelta
from auth import router as auth_router, SECRET_KEY, ALGORITHM, decode_token, hash_password

from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()

app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://kuks-booking.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

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

class CarCreate(BaseModel):
    brand: str
    model: str
    color: str
    seats: int
    price_per_day: float
    car_type: str
    transmission: str
    has_air_conditioning: bool
    year: int
    fuel_type: str
    engine_capacity: float
    mileage: int
    drive_type: str
    supplier_id: int

class ExcursionCreate(BaseModel):
    title: str
    description_en: str | None = None
    description_ru: str | None = None
    duration: str
    location_en: str | None = None
    location_ru: str | None = None
    price: float
    adult_price: float
    child_price: float
    infant_price: float
    operator_id: int


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


# === Admin login & content management ===
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(status_code=401)
    except JWTError:
        raise HTTPException(status_code=401)

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or user.current_token != token:
        raise HTTPException(status_code=401)
    return user


@app.get("/api/admin/excursions")
def admin_excursions(operator_id: int, db: Session = Depends(get_db)):
    return db.query(Excursion).filter(Excursion.operator_id == operator_id).all()

@app.get("/api/admin/cars")
def admin_cars(supplier_id: int, db: Session = Depends(get_db)):
    return db.query(Car).filter(Car.supplier_id == supplier_id).all()

@app.post("/api/admin/cars")
def admin_add_car(car: CarCreate, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current.is_superuser and current.supplier_id != car.supplier_id:
        raise HTTPException(status_code=403)

    db_car = Car(**car.dict())

    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return {"id": db_car.id}

@app.put("/api/admin/cars/{car_id}")
def update_car(car_id: int, updated: CarCreate, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    if not current.is_superuser and current.supplier_id != car.supplier_id:
        raise HTTPException(status_code=403)

    for field, value in updated.dict().items():
        setattr(car, field, value)
    db.commit()
    return {"ok": True}


@app.delete("/api/admin/cars/{car_id}")
def delete_car(car_id: int, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    if not current.is_superuser and current.supplier_id != car.supplier_id:
        raise HTTPException(status_code=403)
    db.delete(car)
    db.commit()
    return {"ok": True}


@app.post("/api/admin/excursions")
def admin_add_excursion(
    excursion: ExcursionCreate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current.is_superuser and current.supplier_id != excursion.operator_id:
        raise HTTPException(status_code=403)

    db_excursion = Excursion(**excursion.dict())
    db.add(db_excursion)
    db.commit()
    db.refresh(db_excursion)
    return {"id": db_excursion.id}

@app.put("/api/admin/excursions/{excursion_id}")
def update_excursion(excursion_id: int, updated: ExcursionCreate, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    excursion = db.query(Excursion).filter(Excursion.id == excursion_id).first()
    if not excursion:
        raise HTTPException(status_code=404, detail="Excursion not found")
    if not current.is_superuser and current.supplier_id != excursion.operator_id:
        raise HTTPException(status_code=403)

    for field, value in updated.dict().items():
        setattr(excursion, field, value)
    db.commit()
    return {"ok": True}


@app.delete("/api/admin/excursions/{excursion_id}")
def delete_excursion(excursion_id: int, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    excursion = db.query(Excursion).filter(Excursion.id == excursion_id).first()
    if not excursion:
        raise HTTPException(status_code=404, detail="Excursion not found")
    if not current.is_superuser and current.supplier_id != excursion.operator_id:
        raise HTTPException(status_code=403)
    db.delete(excursion)
    db.commit()
    return {"ok": True}


@app.get("/api/admin/bookings")
def admin_bookings(supplier_id: int, db: Session = Depends(get_db)):
    return db.query(ConfirmedBooking).filter(ConfirmedBooking.supplier_id == supplier_id).all()

@app.get("/api/suppliers/{supplier_id}")
@app.get("/api/suppliers")
def get_supplier(
    supplier_id: int = None,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current.is_superuser:
        # Суперюзер может смотреть любого поставщика
        if supplier_id is None:
            return db.query(Supplier).all()
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    else:
        # Обычный пользователь может смотреть только себя
        supplier = db.query(Supplier).filter(Supplier.id == current.supplier_id).first()
        # Даже если передали supplier_id — игнорируем его

    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

# === Superuser panel ===

@app.get("/api/super/users")
def super_list_users(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current.is_superuser:
        raise HTTPException(status_code=403)
    return db.query(User).all()

@app.post("/api/super/users")
async def super_add_user(request: Request, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current.is_superuser:
        raise HTTPException(status_code=403)
    data = await request.json()
    user = User(email=data["email"], password_hash=hash_password(data.get("password", "123")), supplier_id=data["supplier_id"])
    db.add(user)
    db.commit()
    return {"ok": True}

@app.post("/api/super/suppliers")
async def super_add_supplier(request: Request, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current.is_superuser:
        raise HTTPException(status_code=403)
    data = await request.json()
    supplier = Supplier(name=data["name"], supplier_type=data["supplier_type"], phone=data.get("phone"), email=data.get("email"), address=data.get("address"))
    db.add(supplier)
    db.commit()
    return {"ok": True}

@app.put("/api/suppliers/{supplier_id}")
async def update_supplier(
    supplier_id: int,
    request: Request,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Обычный пользователь может обновлять только своего поставщика
    if not current.is_superuser and current.supplier_id != supplier_id:
        raise HTTPException(status_code=403, detail="Not allowed to edit this supplier")

    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    data = await request.json()
    supplier.name = data.get("name", supplier.name)
    supplier.phone = data.get("phone", supplier.phone)
    supplier.email = data.get("email", supplier.email)
    supplier.supplier_type = data.get("supplier_type", supplier.supplier_type)
    supplier.address = data.get("address", supplier.address)
    db.commit()

    return {"ok": True}

@app.delete("/api/super/suppliers/{supplier_id}")
def super_delete_supplier(supplier_id: int, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current.is_superuser:
        raise HTTPException(status_code=403)
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    db.delete(supplier)
    db.commit()
    return {"ok": True}

@app.post("/api/admin/change-password")
async def change_password(request: Request, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    data = await request.json()
    new_password = data.get("password")
    if not new_password or len(new_password) < 4:
        raise HTTPException(status_code=400, detail="Invalid password")

    # ✅ Извлекаем user ID из токена
    user_id = decode_token(token)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(new_password)
    db.commit()
    return {"status": "ok"}

@app.put("/api/super/users/{user_id}")
async def super_update_user(user_id: int, request: Request, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current.is_superuser:
        raise HTTPException(status_code=403)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    data = await request.json()

    if "email" in data:
        user.email = data["email"]
    if "password" in data and data["password"]:
        user.password_hash = hash_password(data["password"])
    if "supplier_id" in data:
        user.supplier_id = data["supplier_id"]

    db.commit()
    return {"ok": True}

@app.delete("/api/super/users/{user_id}")
def super_delete_user(user_id: int, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current.is_superuser:
        raise HTTPException(status_code=403)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"ok": True}
