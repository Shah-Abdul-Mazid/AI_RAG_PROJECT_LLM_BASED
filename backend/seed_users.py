from app.db.database import SessionLocal, Base, engine
from app.db.models import User
from app.core.security import get_password_hash

Base.metadata.create_all(bind=engine)

db = SessionLocal()

users = [
    {
        "email": "admin@mgi.org",
        "password": "Admin@123",
        "full_name": "MGI Admin",
        "role": "admin",
    },
    {
        "email": "user@mgi.org",
        "password": "user123",
        "full_name": "MGI Employee",
        "role": "user",
    },
    {
        "email": "admin@nexus.org",
        "password": "Admin2026@",
        "full_name": "Nexus Admin",
        "role": "admin",
    },
    {
        "email": "user@nexus.org",
        "password": "User2026@",
        "full_name": "Nexus User",
        "role": "user",
    },
]

for item in users:
    existing = db.query(User).filter(User.email == item["email"]).first()
    if not existing:
        db.add(User(
            email=item["email"],
            hashed_password=get_password_hash(item["password"]),
            full_name=item["full_name"],
            role=item["role"],
        ))
        print(f"Created user: {item['email']}")
    else:
        print(f"User already exists: {item['email']}")

db.commit()
db.close()
print("Users seeded")
