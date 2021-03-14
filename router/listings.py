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
        db_listing = database.Listing(title=title, author=user.username, context=context)
        db.add(db_listing)
        db.commit()
        db.refresh(db_listing)
    return models.Listing(post_id=str(db_listing.id), title=title, author=user.username, context=context)

@router.get('/get/{id}', status_code=status.HTTP_200_OK, response_model=models.Listing)
def get_listing(id:int, db:database.Session = Depends(database.get_db)):
    listing = db.query(database.Listing).filter_by(id=id).first()
    if listing == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Requested listing not found')
    else:
        return models.Listing(post_id=str(id), title=listing.title, author=listing.author, context=listing.context)


@router.delete('/delete/{id}', status_code=status.HTTP_200_OK)
def delete_listing(id:int, user = Depends(manager), db:database.Session = Depends(database.get_db)):
    db_listing = db.query(database.Listing).filter_by(id=id).first()
    if db_listing == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Requested listing not found')
    elif db_listing.author == user.username:
        db.delete(db_listing)
        db.commit()
        return {'Detail':f'Listing {id} deleted successfully'}
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Not authorized to delete')    
    
@router.put('/update/{id}', status_code=status.HTTP_200_OK, response_model=models.Listing)
def update_listing(id:int, title: str = Form(...), context: str = Form(...), user = Depends(manager), db:database.Session = Depends(database.get_db)):
    listing = db.query(database.Listing).filter_by(id=id).one()
    if listing == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Requested listing not found')
    elif len(title) >= 100:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail='Title too long')
    elif len(context) >= 1000:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail='Context too long')
    elif listing.author == user.username:
        listing.title = title
        listing.context = context
        db.commit()
        return models.Listing(post_id=listing.id, title=listing.title, author=listing.author, context=listing.context)
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Not authorized to update this post')

