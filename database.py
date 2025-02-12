import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure the URL includes `+psycopg2`
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/mydatabase")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
