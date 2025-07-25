from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import config

print("Database URL:", config.DATABASE_URL)

engine = create_engine(
    url=config.DATABASE_URL,
)

local_session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db():
    """ Dependency to get a db sessions """
    db = local_session()
    try:
        yield db
    finally:
        db.close()
    pass