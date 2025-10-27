from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    MONGODB_URI: str
    DB_NAME: str

    class Config:
        env_file = ".env"  # utilisé seulement localement

# Crée une instance globale
settings = Settings(
    MONGODB_URI=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
    DB_NAME=os.getenv("DB_NAME", "kauza_cv_db")
)
