from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class FileMetadata(Base):
    __tablename__ = "file_metadata"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filesize = Column(Integer, nullable=False)
    upload_time = Column(DateTime, default=func.now())
    hmac_hash = Column(String, nullable=False)  
    s3_url = Column(String, nullable=False)
