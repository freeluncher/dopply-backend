from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # Refresh tokens last 7 days
    REFRESH_SECRET_KEY: Optional[str] = None  # Will use SECRET_KEY if not provided

    class Config:
        env_file = ".env"

    @property
    def refresh_secret_key(self) -> str:
        """Return the refresh secret key, defaulting to main SECRET_KEY if not set"""
        return self.REFRESH_SECRET_KEY or self.SECRET_KEY

    def validate_jwt_config(self):
        import logging
        logger = logging.getLogger("jwt_config")
        if not self.SECRET_KEY:
            logger.error("SECRET_KEY is not set! JWT will fail.")
        if not self.ALGORITHM:
            logger.error("ALGORITHM is not set! JWT will fail.")
        logger.info(f"JWT config: SECRET_KEY={self.SECRET_KEY[:6]}... ALGORITHM={self.ALGORITHM}")

settings = Settings()
settings.validate_jwt_config()
