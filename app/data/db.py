from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

DATABASE_URL = f"mysql+pymysql://{settings.DBU}:{settings.DBP}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DBN}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
meta_data = MetaData()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()