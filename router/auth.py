import env, database, models
from fastapi import FastAPI, Depends, HTTPException, status, Response, APIRouter, Form, Request
from starlette.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from datetime import timedelta
from database import Hash
from email_validator import validate_email, EmailNotValidError
from password_strength import PasswordStats

# Router initialization
router = APIRouter(
    tags = ['Auth'],
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
def load_user(username: str,db: database.Session = next(database.get_db())):
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

    token = manager.create_access_token(
        data=dict(sub=username),
        expires=timedelta(days=int(env.EXPIRE_TOKEN_TIME))
    ).decode('utf-8')
    
    res = RedirectResponse(router.url_path_for('user_info'), status_code=status.HTTP_302_FOUND)
    manager.set_cookie(res, token)
    return res


@router.post('/signup', status_code=status.HTTP_200_OK)
def signup(username = Form(...),email = Form(...),password = Form(...), db:database.Session = Depends(database.get_db)):
    if db.query(database.User).filter_by(username=username).first():
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail='Username taken')
    elif db.query(database.User).filter_by(email=email).first():
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail='Email address already in use')
    elif len(username) <= 3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Username must be longer than 3 characters')
    elif len(username) >= 25:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Username is too long. Maximum length: 25 characters')
    elif len(password) <= 8:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Password must be longer than 8 characters')
    elif len(password) >= 20:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Password is too long. Maximum length: 20 characters')
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
        return {'detail':'Account created'}
    



@router.get('/account/info', status_code=status.HTTP_200_OK)
def user_info(user=Depends(manager)):
    if user:
        return {
                'Account':{
                'Username': user.username,
                'Email': user.email,           
                'is_Admin': user.admin,
                }
            }
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')
        
    
@router.get('/logout', status_code=status.HTTP_200_OK)
def logout(response: Response,user = Depends(manager)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')
    else:
        response.delete_cookie('access-token')
        return {'detail': 'Successfully logged out'}