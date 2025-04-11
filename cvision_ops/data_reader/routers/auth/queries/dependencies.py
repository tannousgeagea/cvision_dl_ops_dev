from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from django.contrib.auth import get_user_model
import os

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
ALGORITHM = "HS256"
User = get_user_model()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HTTPException(status_code=401, detail="User not found")

    return user
