import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_NAME: str = "recoleccta"
    DB_USER: str = "root"
    DB_PASS: str = ""
    DB_URL: str | None = None
    MYSQL_PUBLIC_URL: str | None = None
    
    JWT_SECRET: str = "recoleccta-dev-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Mail settings
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_PORT: int = 587
    MAIL_SERVER: str = ""
    MAIL_FROM_NAME: str = "Recoleccta"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def database_url(self) -> str:
        if self.DB_URL:
            return self.DB_URL
        if self.MYSQL_PUBLIC_URL:
            return self.MYSQL_PUBLIC_URL
        
        password_part = f":{self.DB_PASS}" if self.DB_PASS else ""
        return f"mysql+pymysql://{self.DB_USER}{password_part}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

settings = Settings()
