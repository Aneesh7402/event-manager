# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import db_settings  # Import the db_settings object


# Form the database URL by combining the fields from the db_settings object
# app/db/session.py or app/config.py


engine = create_engine(db_settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
