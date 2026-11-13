import os


DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///tasks.db")
SECRET_KEY = os.environ.get("APP_SECRET_KEY") or os.urandom(32).hex()
DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
CORS_ORIGINS = [origin.strip() for origin in os.environ.get("CORS_ORIGINS", "").split(",") if origin.strip()]
