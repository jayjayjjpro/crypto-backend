import boto3
import os
import hmac
import hashlib
from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import FileMetadata, Base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Create database tables (if they don't exist)
Base.metadata.create_all(bind=engine)

# AWS S3 Configuration
S3_BUCKET = os.getenv("AWS_S3_BUCKET_NAME")
S3_REGION = os.getenv("AWS_S3_REGION")
S3_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
S3_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

s3_client = boto3.client(
    "s3",
    region_name=S3_REGION,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY
)

# Function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Secret key for HMAC (Change this in production!)
SECRET_KEY = b"supersecretkey"

# API Endpoint: Upload File to S3
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_content = await file.read()
    
    # Generate HMAC hash for file integrity
    hmac_hash = hmac.new(SECRET_KEY, file_content, hashlib.sha256).hexdigest()

    # Upload file to S3
    s3_file_path = f"uploads/{file.filename}"
    s3_client.put_object(Bucket=S3_BUCKET, Key=s3_file_path, Body=file_content)

    # Store file metadata in PostgreSQL
    s3_file_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_file_path}"
    
    new_file = FileMetadata(
        filename=file.filename,
        filesize=len(file_content),
        hmac_hash=hmac_hash,
        s3_url=s3_file_url  
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    return {
        "message": "File uploaded to S3 successfully",
        "filename": file.filename,
        "filesize": len(file_content),
        "hmac_hash": hmac_hash,
        "s3_url": s3_file_url
    }
