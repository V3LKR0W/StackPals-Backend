from fastapi import APIRouter, status, Depends
from .auth import manager

router = APIRouter(
    tags = ['Listings'],
    prefix = '/v1/listing'
)

@router.post('/create', status_code=status.HTTP_200_OK)
def protected(user = Depends(manager)):
    return 'a'