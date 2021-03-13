from pydantic import BaseModel, Field

class User(BaseModel):
    username: str = Field(..., example='username')
    email: str = Field(..., example='ex@email.com')
    password: str = Field(..., example='password')
    class Config: 
        orm_mode = True
        
class Listing(BaseModel):
    title: str = Field(..., example='Cool listing title')
    context: str = Field(..., example='Interesting context')
    class Config: 
        orm_mode = True