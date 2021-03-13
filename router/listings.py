from fastapi import APIRouter, status, Depends, Form, status, HTTPException
from .auth import manager
import database, models


router = APIRouter(
    tags = ['Listings'],
    prefix = '/v1/listing'
)

@router.post('/create', status_code=status.HTTP_200_OK, response_model=models.Listing)
def create_listing(title: str = Form(...), context: str = Form(...), user = Depends(manager), db:database.Session = Depends(database.get_db)):
    if len(title) >= 100:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail='Title too long')
    elif len(context) >= 1000:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail='Context too long')
    else:
        db_listing = database.Listing(title=title, context=context)
        db.add(db_listing)
        db.commit()
        db.refresh(db_listing)
    
    return models.Listing(title=title, context=context)