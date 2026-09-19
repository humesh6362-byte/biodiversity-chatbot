from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ollama_model: str = "llama3.2:3b"
    chroma_persist_dir: str = "./chroma_db"
    cors_origins: str = "http://localhost:5500"

    class Config:
        env_file = ".env"


settings = Settings()