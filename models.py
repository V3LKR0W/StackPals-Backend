from pydantic import BaseModel, Field

# User model

class User(BaseModel):
    username: str = Field(..., example='username')
    email: str = Field(..., example='ex@email.com')
    password: str = Field(..., example='password')
    class Config: 
        orm_mode = True
        
# Listing model        
        
class ListingBase(BaseModel):
    title: str = Field(..., example='Cool listing title')
    author: str = Field(..., example='user_name')
    context: str = Field(..., example='Interesting context')
    class Config: 
        orm_mode = True
    
class Listing(ListingBase):
    title: str = Field(..., example='Listing title')
    id: str = Field(..., example='Listing ID')
    author: str = Field(..., example='Listing author')
    context: str = Field(..., example='Listing context')
    class Config: 
        orm_mode = True