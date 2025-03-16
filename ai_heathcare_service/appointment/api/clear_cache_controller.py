
from functools import lru_cache
from fastapi import APIRouter, Depends

from appointment.core.db import TokenData, get_current_user


router = APIRouter()

@lru_cache(maxsize=100)
def cached_function(value: int):
    return value * 2  # Just an example function

@router.get("/clear-cache")
def clear_cache(user: TokenData = Depends(get_current_user)):
    cached_function.cache_clear()
    return {"message": "Cache cleared"}