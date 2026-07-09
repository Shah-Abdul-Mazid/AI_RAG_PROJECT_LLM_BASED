"""
Database Seeder Script
======================
Seeds default Admin and User accounts into the PostgreSQL database.
Run this ONCE after switching to PostgreSQL:

    cd backend
    python seed.py

"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import Base, engine, SessionLocal
from app.db import models
from app.core.security import get_password_hash

# ─── Define your default seed users here ──────────────────────────────────────
SEED_USERS = [
    {
        "full_name": "MGI Admin",
        "email": "admin@nexus.com",
        "password": "Admin@1234",
        "role": "admin",
    },
    {
        "full_name": "Shah Abdul Mazid",
        "email": "shah@nexus.com",
        "password": "User@1234",
        "role": "user",
    },
    {
        "full_name": "Demo User",
        "email": "demo@nexus.com",
        "password": "Demo@1234",
        "role": "user",
    },
    {
        "full_name": "Nexus Admin",
        "email": "admin@nexus.org",
        "password": "Admin2026@",
        "role": "admin",
    },
    {
        "full_name": "Nexus User",
        "email": "user@nexus.org",
        "password": "User2026@",
        "role": "user",
    },
]
# ──────────────────────────────────────────────────────────────────────────────


def seed():
    print("🌱 Creating tables in PostgreSQL (if not already created)...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables ready.")

    db = SessionLocal()
    seeded = 0
    skipped = 0

    try:
        for user_data in SEED_USERS:
            # Check if user already exists
            existing = db.query(models.User).filter(
                models.User.email == user_data["email"]
            ).first()

            if existing:
                print(f"⏭️  Skipped (already exists): {user_data['email']}")
                skipped += 1
                continue

            # Create new user with hashed password
            new_user = models.User(
                full_name=user_data["full_name"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"],
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            print(f"✅ Created [{user_data['role'].upper()}]: {user_data['email']} (password: {user_data['password']})")
            seeded += 1

    except Exception as e:
        db.rollback()
        print(f"❌ Error during seeding: {e}")
        raise
    finally:
        db.close()

    print(f"\n🎉 Seeding complete! {seeded} users created, {skipped} skipped.")
    print("\n📋 Login credentials:")
    print("─" * 45)
    for u in SEED_USERS:
        print(f"  [{u['role'].upper():5}] {u['email']} / {u['password']}")
    print("─" * 45)


if __name__ == "__main__":
    seed()
