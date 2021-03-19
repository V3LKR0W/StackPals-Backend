import env, database, models
from fastapi import FastAPI, Depends, HTTPException, status, Response, APIRouter, Form, Request
from typing import Optional
from starlette.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from datetime import timedelta
from database import Hash, User
from email_validator import validate_email, EmailNotValidError
from password_strength import PasswordStats

# Router initialization
router = APIRouter(
    tags = ['Authentication'],
    prefix = '/v1/auth',
)

# Session Manager initialization
manager = LoginManager(
    secret=env.SECRET_KEY,
    tokenUrl="/auth/login",
    use_cookie=True,
    use_header=False,
   )

@manager.user_loader
def load_user(username: str, db: database.Session = next(database.get_db())):
    return db.query(database.User).filter_by(username=username).first()


# Routes

@router.post('/login')
def login(data: OAuth2PasswordRequestForm = Depends()):
    username = data.username
    password = data.password

    user = load_user(username)
    if not user:
        raise HTTPException(status_code=404, detail='Wrong username or password')
    elif Hash.verify_password(password, user.password) == False:
        raise HTTPException(status_code=404, detail='Wrong username or password')
    elif user.banned == 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Banned account')
    else:
        token = manager.create_access_token(
            data=dict(sub=username),
            expires=timedelta(days=int(env.EXPIRE_TOKEN_TIME))
        ).decode('utf-8')
        
        res = RedirectResponse(router.url_path_for('user_info'), status_code=status.HTTP_302_FOUND)
        manager.set_cookie(res, token)
        return res


@router.post('/signup',  status_code=status.HTTP_200_OK, response_model=models.User)
def signup(username = Form(...), email = Form(...), password = Form(...), db:database.Session = Depends(database.get_db)):
    if db.query(database.User).filter_by(username=username).first():
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail='Username taken')
    elif db.query(database.User).filter_by(email=email).first():
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail='Email address already in use')
    elif len(username) <= 3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Username must be longer than 3 characters')
    elif len(username) >= 25:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Username is too long. Maximum length: 25 characters')
    elif len(password) < 7:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Password must be 8 characters or more')
    elif len(password) >= 40:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Password is too long. Maximum length: 40 characters')
    elif PasswordStats(password).strength() <= float(0.350):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Password is not strong enough. Try adding some symbols or numbers your password')
    elif len(email) >= 75:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Email is too long. Must be less than 75 characters')
    try:
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Email address not supported. Please use another email.')
    else:
        pwd_hash = Hash.get_password_hash(str(password))
        db_user = database.User(username=username,email=email,password=pwd_hash)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return models.User(username=username,email=email,password=password)
    


@router.get('/account/info', status_code=status.HTTP_200_OK)
def user_info(user=Depends(manager)):
    if user:
        return {
                'Account':{
                'Username': user.username,
                'Email': user.email,           
                'is_Admin': user.admin,
                'is_Banned': user.banned,
                }
            }
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')
        
    
@router.get('/logout', status_code=status.HTTP_200_OK)
def logout(response: Response, user = Depends(manager)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')
    else:
        response.delete_cookie('access-token')
        return {'detail': 'Successfully logged out'}
    

@router.put('/account/update/password', status_code=status.HTTP_200_OK)
def update_password(current_password = Form(...), new_password = Form(...), user = Depends(manager), db:database.Session = Depends(database.get_db)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')
    elif len(new_password) < 7:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Password must be 8 characters or more')
    elif len(new_password) >= 40:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Password is too long. Maximum length: 40 characters')
    elif PasswordStats(new_password).strength() <= float(0.350):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Password is not strong enough. Try adding some symbols or numbers your password')
    else:
        db_user = db.query(database.User).filter_by(username=user.username).first()
        if database.Hash.verify_password(current_password, db_user.password):
            db_user.password = database.Hash.get_password_hash(new_password)
            db.commit()
            db.refresh(db_user)
            return {'detail': 'Passwored changed'}
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Current password is incorrect')
        
@router.put('/account/update/email', status_code=status.HTTP_200_OK)
def update_email(email = Form(...), user = Depends(manager), db:database.Session = Depends(database.get_db)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')
    else:
        if len(email) >= 75:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Email is too long')
        else:
            db_user = db.query(database.User).filter_by(username=user.username).first()
            db_user.email = email
            db.commit()
            db.refresh(db_user)
            return {'detail', 'Email successfully changed'}
        
@router.delete('/account/delete', status_code=status.HTTP_200_OK)
def delete_account(password = Form(...), user = Depends(manager), db:database.Session = Depends(database.get_db)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')
    else:
        db_user = db.query(database.User).filter_by(username=user.username).first()
        if database.Hash.verify_password(password, db_user.password):
            db.delete(db_user)
            db.commit()
            return {'detail': 'Account deleted successfully.'}      
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Account password is incorrect')
    
    