from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from appointment.core import jwt

# DATABASE_URL = "postgresql+asyncpg://user:password@localhost/hospital_db"

# engine = create_async_engine(DATABASE_URL, echo=True)
# AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# async def get_db():
#     async with AsyncSessionLocal() as session:
#         yield session

# Database connection

Base = declarative_base()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

DATABASE_URL = "postgresql://postgres:123456@localhost/hospital_db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TokenData(BaseModel):
    username: Optional[str] = None        
        
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        token_data = TokenData(username=username)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return token_data