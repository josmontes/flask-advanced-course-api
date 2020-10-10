import os


DEBUG = False
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///data.db")
