from fastapi import APIRouter, Depends, HTTPException
from models import User, Supplier
from database import SessionLocal
from auth import get_current_user

router = APIRouter(prefix="/api/super")

@router.get("/users")
def list_users(current: User = Depends(get_current_user)):
    if not current.is_superuser:
        raise HTTPException(status_code=403)
    db = SessionLocal()
    return db.query(User).all()

@router.post("/users")
def add_user(data: dict, current: User = Depends(get_current_user)):
    if not current.is_superuser:
        raise HTTPException(status_code=403)
    db = SessionLocal()
    user = User(email=data["email"], password_hash="123", supplier_id=data["supplier_id"])
    db.add(user)
    db.commit()
    return {"ok": True}

@router.get("/suppliers")
def list_suppliers(current: User = Depends(get_current_user)):
    if not current.is_superuser:
        raise HTTPException(status_code=403)
    db = SessionLocal()
    return db.query(Supplier).all()

@router.post("/suppliers")
def add_supplier(data: dict, current: User = Depends(get_current_user)):
    if not current.is_superuser:
        raise HTTPException(status_code=403)
    db = SessionLocal()
    supplier = Supplier(name=data["name"], type=data["type"])
    db.add(supplier)
    db.commit()
    return {"ok": True}
