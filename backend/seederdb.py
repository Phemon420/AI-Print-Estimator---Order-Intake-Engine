from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from main import config_postgres_url

Base = declarative_base()

# 1. Create the engine globally so it can be imported by Alembic and Seeders
engine = create_engine(
    config_postgres_url,
    pool_size=50,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_timeout=60
)

# 2. Create the SessionLocal factory globally
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def function_client_read_postgres(database_url: str):
    """
    This remains for your lifespan logic if you prefer dynamic initialization,
    but the global SessionLocal above is better for standard tools.
    """
    with engine.connect() as conn:
        pass 
    return SessionLocal