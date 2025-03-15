
from functools import lru_cache
from fastapi import APIRouter


router = APIRouter()

@lru_cache(maxsize=100)
def cached_function(value: int):
    return value * 2  # Just an example function

@router.get("/clear-cache")
def clear_cache():
    cached_function.cache_clear()
    return {"message": "Cache cleared"}