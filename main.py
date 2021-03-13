from fastapi import FastAPI
from router import auth, listings

app = FastAPI()

app.include_router(auth.router)
app.include_router(listings.router)