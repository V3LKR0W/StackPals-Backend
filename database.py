from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext

SQLALCHEMY_DATABASE_URL = 'sqlite:///./app.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Tables

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String, unique=False)
    admin = Column(Boolean, default=False)
    banned = Column(Boolean, default=False)

class Listing(Base):
    __tablename__ = 'listing'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=False) 
    body = Column(String, unique=False)
    
# Hashing

class Hash():
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(password):
        return pwd_context.hash(password)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
Base.metadata.create_all(engine)