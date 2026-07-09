from datetime import timedelta

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pymongo.database import Database
from pydantic import BaseModel, EmailStr

from app.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.db.database import get_db
from app.db.models import User

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    full_name: str


@router.post("/register")
async def register_user(payload: RegisterRequest, db: Database = Depends(get_db)):
    email = payload.email.strip().lower()
    # Check if email already exists
    existing = db["users"].find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Insert new user document
    doc = User.new_doc(
        email=email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        role="user",
    )
    result = db["users"].insert_one(doc)
    user_id = str(result.inserted_id)

    return {
        "message": "User registered successfully",
        "id": user_id,
        "email": email,
        "full_name": payload.full_name,
        "role": "user",
    }


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Database = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    doc = db["users"].find_one({"email": email.strip().lower()})
    if doc is None:
        raise credentials_exception

    return User(doc)


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Database = Depends(get_db),
):
    email = form_data.username.strip().lower()
    print(f"[AUTH] Login attempt for: {email}")
    
    doc = db["users"].find_one({"email": email})
    
    if not doc:
        print(f"[AUTH] Login failed: User not found for email '{email}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    password_verified = verify_password(form_data.password, doc["hashed_password"])
    if not password_verified:
        print(f"[AUTH] Login failed: Password verification failed for email '{email}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print(f"[AUTH] Login successful for: {email} ({doc.get('role')})")
    user = User(doc)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "full_name": user.full_name,
    }


@router.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
    }
