from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings


DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, bind=engine, expire_on_commit=False)
Base = declarative_base()


def get_db():
    """This function is a generator that provides a database session to the caller.
    It creates a new session, yields it to the caller, and ensures that the session is properly closed after use.
    If any SQLAlchemyError occurs during the session, it rolls back the transaction and raises the error.

    Yields:
        _type_: A SQLAlchemy session object that can be used to interact with the database.
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError:
        db.rollback()
        raise
    finally:
        db.close()
