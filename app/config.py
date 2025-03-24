from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""

    API_TITLE: str = "Social Media Recommendation API"
    API_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"

    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DBN: str
    DBU: str
    DBP: str

    CACHE_TTL: int = 3600

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()