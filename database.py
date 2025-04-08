import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load DB URL from env or use default PostgreSQL connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/mydatabase")

# Create SQLAlchemy engine for DB connection
engine = create_engine(DATABASE_URL)

# Create a session factory for DB operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
