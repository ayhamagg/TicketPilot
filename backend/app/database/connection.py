from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings


# The engine is the actual connection to PostgreSQL
# It uses the DATABASE_URL from our .env file
engine = create_engine(settings.DATABASE_URL)

# SessionLocal is a factory that creates new database sessions
# autocommit=False means we control when changes are saved
# autoflush=False means we control when changes are sent to the DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base class that all our database models will inherit from
class Base(DeclarativeBase):
    pass


# This function is used by FastAPI routes to get a database session
# It opens a session, gives it to the route, then closes it when done
# The "yield" makes it work as a FastAPI dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()