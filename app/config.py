from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    MONGODB_URI: str
    DB_NAME: str
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    gemini_api_key: str
    class Config:
        env_file = ".env"  

# Crée une instance globale
settings = Settings(
    
)
