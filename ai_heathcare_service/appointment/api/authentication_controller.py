from datetime import datetime, timedelta
from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
import redis
from sqlalchemy.orm import Session

from appointment.core import jwt
from appointment.core.db import get_db
from appointment.core.jwt import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from appointment.dto import Token, UserPatientCreate
from appointment.models import User
from appointment.repository import user_repository
from appointment.service import user_service
from appointment.core.db import oauth2_scheme

router = APIRouter()

# redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# login
@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_repository.verify_user(db, form_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# sign up
@router.post("/users/")
def create_user(user: UserPatientCreate, db: Session = Depends(get_db)):
    db_user = user_service.get_user_username_phone_logic(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return user_service.create_user_logic(db=db, user=user)


# @router.post("/logout")
# async def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     try:
#         payload = jwt.decode_token(token)
#         exp = payload.get("exp")
#         jti = payload.get("jti")  # JWT ID
#         current_time = datetime.utcnow()
#         ttl = exp - int(current_time.timestamp())
#         if ttl > 0:
#             redis_client.setex(f"blacklist:{jti}", ttl, "true")
#         return {"message": "Logged out successfully"}
#     except JWTError:
#         raise HTTPException(status_code=400, detail="Invalid token")

