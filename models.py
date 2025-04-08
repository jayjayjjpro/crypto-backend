from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  # Base class for model definitions

class FileMetadata(Base):
    __tablename__ = "file_metadata"  # DB table name

    id = Column(Integer, primary_key=True, index=True)  # Primary key with index
    filename = Column(String, nullable=False)  # Original filename
    filesize = Column(Integer, nullable=False)  # Size in bytes
    upload_time = Column(DateTime, default=func.now())  # Auto timestamp
    hmac_hash = Column(String, nullable=False)  # HMAC for integrity
    s3_url = Column(String, nullable=False)  # Link to file in S3
