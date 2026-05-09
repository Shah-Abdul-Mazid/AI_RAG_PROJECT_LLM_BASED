from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from jose import JWTError, jwt
from app.core.security import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# --- Fake Database for Demo Purposes ---
# In a real enterprise app, this would be in PostgreSQL
USERS_DB = {
    "admin@mgi.org": {
        "username": "admin@mgi.org",
        "email": "admin@mgi.org",
        "full_name": "MGI Admin",
        "role": "admin",
        "hashed_password": "PASTE_ADMIN_HASH_HERE",
    },
    "user@mgi.org": {
        "username": "user@mgi.org",
        "email": "user@mgi.org",
        "full_name": "MGI Employee",
        "role": "user",
        "hashed_password": "PASTE_USER_HASH_HERE",
    }
}

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    full_name: str

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = USERS_DB.get(username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = USERS_DB.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "role": user["role"],
        "full_name": user["full_name"]
    }

@router.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    # Returns the current user's profile minus the password
    return {
        "username": current_user["username"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "role": current_user["role"]
    }
