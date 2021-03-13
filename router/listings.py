from fastapi import APIRouter, status, Depends, Form
from .auth import manager
import database, models


router = APIRouter(
    tags = ['Listings'],
    prefix = '/v1/listing'
)

@router.post('/create', status_code=status.HTTP_200_OK, response_model=models.Listing)
def protected(title: str = Form(...), context: str = Form(...), user = Depends(manager), db:database.Session = Depends(database.get_db)):
    
    
    
    return models.Listing(title=title, context=context)