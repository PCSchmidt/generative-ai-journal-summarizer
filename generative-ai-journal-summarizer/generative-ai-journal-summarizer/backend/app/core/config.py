from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Journal Summarizer"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    HUGGINGFACE_API_KEY: Optional[str] = os.getenv("HUGGINGFACE_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    
    # Vector Database
    VECTOR_DB_PATH: str = "./data/vector_store"
    EMBEDDINGS_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]  # Configure for production
    
    # File Upload
    UPLOAD_PATH: str = "./data/uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"

settings = Settings()
