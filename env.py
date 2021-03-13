import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
EXPIRE_TOKEN_TIME = os.getenv("EXPIRE_TOKEN_TIME")
