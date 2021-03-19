from os import stat
from fastapi import APIRouter, Depends, status, Form, HTTPException
from typing import List
from .auth import manager
import database, models
import time

router = APIRouter(
    tags=['Message'],
    prefix='/v1/message'
)

@router.post('/send', status_code=status.HTTP_200_OK, response_model=models.Message)
def send_message(recipent = Form(...), header = Form(...), body = Form(...), user=Depends(manager), db:database.Session = Depends(database.get_db)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')
    elif len(header) >= 25:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Message header cannot be more than 100 characters')
    elif len(body) >= 1000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detial='Message body cannot be more than 1000 characters')
    else:
        to = db.query(database.User).filter_by(username=recipent).first()
        if to == None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Recipent of message not found')
        else:
            db_message = database.Messages(sent_at=time.time(), sent_by=user.username, recipent=recipent, header=header, body=body)
            db.add(db_message)
            db.commit()
            return models.Message(sent_at=time.time(),sent_by=user.username, recipent=recipent, header=header, body=body)
        
@router.get('/inbox', status_code=status.HTTP_200_OK)
def inbox(user=Depends(manager), db:database.Session = Depends(database.get_db)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')
    else:
        inbox = db.query(database.Messages).filter_by(recipent=user.username).all()
        return inbox    
    