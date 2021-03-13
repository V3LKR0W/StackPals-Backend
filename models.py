from pydantic import BaseModel, Field

class User(BaseModel):
    username: str = Field(..., example='username')
    email: str = Field(..., example='ex@email.com')
    password: str = Field(..., example='password')
    class Config: 
        orm_mode = True
        
class Listing(BaseModel):
    title: str 
    poster: str
    body: str
    class Config: 
        orm_mode = True