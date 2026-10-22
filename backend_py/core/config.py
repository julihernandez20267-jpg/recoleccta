import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

class Settings(BaseSettings):
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_NAME: str = "recoleccta"
    DB_USER: str = "root"
    DB_PASS: str = ""
    DB_URL: str | None = None
    MYSQL_PUBLIC_URL: str | None = None
    DB_SSL_CA: str | None = None
    
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
    def database_url(self) -> str | URL:
        if self.DB_URL:
            return self.DB_URL
        if self.MYSQL_PUBLIC_URL:
            return self.MYSQL_PUBLIC_URL

        return URL.create(
            "mysql+pymysql",
            username=self.DB_USER,
            password=self.DB_PASS or None,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
            query={"charset": "utf8mb4"},
        )

settings = Settings()
