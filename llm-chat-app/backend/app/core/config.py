import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./llm_chat.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "please_change_me")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_SECONDS: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", "3600"))

    # Qdrant
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY: str | None = os.getenv("QDRANT_API_KEY", None)
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "documents")

    # Gemini (user-provided)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_API_URL: str = os.getenv("GEMINI_API_URL", "https://api.gemini-your-endpoint/v1")  # replace if needed

    # Embedding model name / endpoint (depends on provider)
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "gemini-embed-1")

settings = Settings()
