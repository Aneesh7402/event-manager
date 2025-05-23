from app.db.base import Base
from app.db.session import engine

# Import all models here before create_all
from app.db.models.auth import user

def init_db():
    Base.metadata.create_all(bind=engine)