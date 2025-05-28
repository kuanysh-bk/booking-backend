from fastapi import APIRouter, Depends
from models import User
from auth import get_current_user

router = APIRouter(prefix="/api/admin")

@router.post("/login")
def login(data: dict):
    from models import User
    from database import SessionLocal
    from auth import create_access_token
    db = SessionLocal()
    user = db.query(User).filter(User.email == data["email"]).first()
    if not user or user.password_hash != data["password"]:
        return {"error": "Invalid credentials"}
    token = create_access_token({"sub": str(user.id)})
    return {"token": token, "is_superuser": user.is_superuser}

@router.get("/excursions")
def get_excursions(user: User = Depends(get_current_user)):
    from models import Excursion
    from database import SessionLocal
    db = SessionLocal()
    return db.query(Excursion).filter(Excursion.supplier_id == user.supplier_id).all()
