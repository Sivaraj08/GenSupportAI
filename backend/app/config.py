import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "GenSupportAI"
    
    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./gensupport.db")
    
    # Storage Settings
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    CHROMA_DB_DIR: str = os.getenv("CHROMA_DB_DIR", "./chroma_db")
    
    # RAG Settings
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 800))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 150))
    
    # LLM Settings
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemma2:9b") # fallback to llama3 if desired
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", 90))

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)
