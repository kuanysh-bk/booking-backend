from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def main():
    db: Session = SessionLocal()
    users = db.query(User).all()

    updated = 0
    for user in users:
        if user.password_hash and not user.password_hash.startswith("$2b$"):
            print(f"🔐 Hashing password for: {user.email}")
            user.password_hash = hash_password(user.password_hash)
            updated += 1

    db.commit()
    db.close()
    print(f"✅ Done. {updated} password(s) updated.")

if __name__ == "__main__":
    main()