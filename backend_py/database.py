import ssl
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

connect_args = {}
if settings.DB_SSL_CA:
    connect_args["ssl"] = ssl.create_default_context(cadata=settings.DB_SSL_CA)

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
