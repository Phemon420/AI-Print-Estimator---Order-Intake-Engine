from package import *

Base = declarative_base()

def function_client_read_postgres(database_url: str):
    """
    Initializes the SQLAlchemy engine and returns the SessionLocal factory.
    """
    engine = create_engine(
        database_url,
        pool_size=50,
        max_overflow=30,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_timeout=60
    )
    # Testing the connection immediately
    with engine.connect() as conn:
        pass 
        
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)