import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./data.db"

# Scalable engine configuration with optimized SQLite
engine = create_engine(
    DATABASE_URL, 
    connect_args={
        "check_same_thread": False,
        "timeout": 30  # Timeout to avoid long locks
    },
    # For SQLite: StaticPool is the correct option for concurrency
    poolclass=StaticPool,
    echo=False  # True for SQL debug
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """Initializes the database with logging."""
    try:
        from app.models import Sale
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def get_session():
    """Gets database session from connection pool."""
    return SessionLocal()

def get_db():
    """Generator for dependency injection in FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_health() -> bool:
    """Verifica la salud de la base de datos."""
    try:
        session = get_session()
        session.execute(text("SELECT 1"))
        session.close()
        return True
    except Exception as e:
        logger.error(f"Error en health check de DB: {e}")
        return False
