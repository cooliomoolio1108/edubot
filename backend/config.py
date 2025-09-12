# config.py
from dotenv import load_dotenv
import os

load_dotenv()  # Load from .env

class Config:
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    MONGO_URI = os.getenv("MONGO_URI")
    AUTHORITY = "https://login.microsoftonline.com/common"
    REDIRECT_PATH = "auth/getAuth"
    SCOPE = ["User.Read"]
    FRONTEND_URL = os.getenv("STREAMLIT_URL")
    JWT_SECRET = os.getenv("JWT_SECRET")
    CALLBACK_URL = os.getenv("CALLBACK")

