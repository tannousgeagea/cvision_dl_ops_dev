from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.conf import settings
from jose import jwt
import os

# Django settings for JWT
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")  # Use Django's secret key or create a separate key
ALGORITHM = "HS256"

router = APIRouter()

# Login request model
class LoginRequest(BaseModel):
    email: str
    password: str

# Login response model
class LoginResponse(BaseModel):
    access_token: str
    token_type: str

# Generate JWT token
def create_access_token(user_id: int):
    payload = {
        "user_id": user_id,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

# Login API
@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest):
    user = authenticate(username=data.email, password=data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Update last login
    update_last_login(None, user)

    # Generate JWT token
    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
