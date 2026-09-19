from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    chat_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    chroma_persist_dir: str = "./chroma_db"
    cors_origins: str = "http://localhost:5500"

    class Config:
        env_file = ".env"


settings = Settings()
