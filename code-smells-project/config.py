import os


SECRET_KEY = os.environ.get("APP_SECRET_KEY")
DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
