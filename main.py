import boto3
from botocore.exceptions import ClientError
import os
import hmac
import hashlib
from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import FileMetadata, Base
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# Import AWS Cognito authentication module
from auth import router as auth_router, add_auth_middleware


# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI()


# Add session management middleware (for Cognito authentication)
add_auth_middleware(app)

# Include authentication routes
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow frontend requests (Change * to specific domain in prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

# API Endpoint: List All Uploaded Files
# @app.get("/files/")
# async def list_files(db: Session = Depends(get_db)):
#     files = db.query(FileMetadata).all()
#     return files

@app.get("/files/")
async def list_files(db: Session = Depends(get_db)):
    files = db.query(FileMetadata).all()
    valid_files = []

    for file in files:
        s3_file_path = f"uploads/{file.filename}"
        
        try:
            s3_client.head_object(Bucket=S3_BUCKET, Key=s3_file_path)  # Check if file exists in S3
            valid_files.append(file)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                db.delete(file)
                db.commit()

    return valid_files


@app.get("/files/{filename}/download/")
async def generate_presigned_url(filename: str):
    s3_file_path = f"uploads/{filename}"
    
    try:
        # Generate a pre-signed URL
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET, "Key": s3_file_path},
            ExpiresIn=3600  # 1 hour expiration time
        )
        return {"presigned_url": presigned_url}
    except Exception as e:
        return {"error": str(e)}

@app.get("/files/{filename}/verify/")
async def verify_file_integrity(filename: str, db: Session = Depends(get_db)):
    # Retrieve the file metadata from PostgreSQL
    file_metadata = db.query(FileMetadata).filter(FileMetadata.filename == filename).first()

    if not file_metadata:
        return {"error": "File not found in database"}

    # Download file from S3
    s3_file_path = f"uploads/{filename}"

    try:
        s3_response = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_file_path)
        file_content = s3_response["Body"].read()
    except Exception as e:
        return {"error": f"Failed to fetch file from S3: {str(e)}"}

    # Recalculate HMAC hash
    recalculated_hmac = hmac.new(SECRET_KEY, file_content, hashlib.sha256).hexdigest()

    # Compare with stored HMAC
    is_valid = recalculated_hmac == file_metadata.hmac_hash

    return {
        "filename": filename,
        "stored_hmac": file_metadata.hmac_hash,
        "recalculated_hmac": recalculated_hmac,
        "is_valid": is_valid
    }


@app.delete("/files/{filename}/delete/")
async def delete_file(filename: str, db: Session = Depends(get_db)):
    s3_file_path = f"uploads/{filename}"

    # Delete from S3
    try:
        s3_client.delete_object(Bucket=S3_BUCKET, Key=s3_file_path)
    except ClientError as e:
        return {"error": f"Failed to delete from S3: {str(e)}"}

    # Delete from database
    file_metadata = db.query(FileMetadata).filter(FileMetadata.filename == filename).first()
    if file_metadata:
        db.delete(file_metadata)
        db.commit()

    return {"message": f"File '{filename}' deleted successfully from S3 and database"}


