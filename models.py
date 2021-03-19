from database import Base
from pydantic import BaseModel, Field

# User model

class User(BaseModel):
    username: str = Field(..., example='username')
    email: str = Field(..., example='ex@ample.com')
    password: str = Field(..., example='password')
    class Config: 
        orm_mode = True
        
# Listing model        
        
class Listing(BaseModel):
    post_id: int = Field(..., example='Listing ID')
    created_at: int = Field(..., example='Listing timestamp')
    title: str = Field(..., example='Listing title')
    author: str = Field(..., example='Listing author')
    context: str = Field(..., example='Listing context')
    class Config: 
        orm_mode = True
        
        
# Message model

class Message(BaseModel):
    sent_at: int = Field(..., example='Message timestamp')
    sent_by: str = Field(..., example='Who sent the message')
    recipent: str = Field(..., example='Message reciver')
    header: str = Field(..., example='Message header')
    body: str = Field(..., example='Messsage body') 
    class Config: 
        orm_mode = True      