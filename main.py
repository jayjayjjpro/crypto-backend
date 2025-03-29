import os
import hmac
import hashlib
import base64
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from botocore.exceptions import ClientError
import boto3
from fastapi.responses import Response
from dotenv import load_dotenv

from database import SessionLocal, engine
from models import FileMetadata, Base
# from auth import router as auth_router, add_auth_middleware

# New: Encryption utilities
from utils.crypto_utils import encrypt_file, decrypt_file
from utils.kms_utils import encrypt_key_with_kms, decrypt_key_with_kms
from utils.gcs_utils import upload_to_gcs, download_from_gcs, delete_from_gcs

# Load env vars & set up GCP auth
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


# Initialize FastAPI
app = FastAPI()
# add_auth_middleware(app)
# app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables if not exist
Base.metadata.create_all(bind=engine)

# AWS S3 config
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

# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Secret for HMAC
SECRET_KEY = b"supersecretkey"


# API Endpoint: Upload File to S3
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_content = await file.read()

    existing_file = db.query(FileMetadata).filter(FileMetadata.filename == file.filename).first()
    if existing_file:
        return {"error": "File already exists", "filename": existing_file.filename, "s3_url": existing_file.s3_url}

    # Encrypt the file
    encrypted_file, aes_key, nonce = encrypt_file(file_content)

    # Encrypt AES key with Google KMS
    encrypted_key = encrypt_key_with_kms(aes_key)
    gcs_key_path = f"encrypted-keys/{file.filename}.key.enc"
    upload_to_gcs(gcs_key_path, encrypted_key)

    # Upload encrypted file to S3
    s3_file_path = f"uploads/{file.filename}"
    s3_client.put_object(Bucket=S3_BUCKET, Key=s3_file_path, Body=encrypted_file)

    # HMAC for integrity
    hmac_hash = hmac.new(SECRET_KEY, encrypted_file, hashlib.sha256).hexdigest()
    s3_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_file_path}"

    # Store metadata
    new_file = FileMetadata(
        filename=file.filename,
        filesize=len(file_content),
        hmac_hash=hmac_hash,
        s3_url=s3_url
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    return {
        "message": "Encrypted file uploaded to S3",
        "filename": file.filename,
        "filesize": len(file_content),
        "hmac_hash": hmac_hash,
        "s3_url": s3_url
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


from fastapi.responses import StreamingResponse
import io
import mimetypes

@app.get("/files/{filename}/download/")
async def download_file(filename: str):
    try:
        encrypted_file = s3_client.get_object(Bucket=S3_BUCKET, Key=f"uploads/{filename}")["Body"].read()
        encrypted_key = download_from_gcs(f"encrypted-keys/{filename}.key.enc")
        aes_key = decrypt_key_with_kms(encrypted_key)
        decrypted_file = decrypt_file(encrypted_file, aes_key)

        mime_type, _ = mimetypes.guess_type(filename)

        return StreamingResponse(
            io.BytesIO(decrypted_file),
            media_type=mime_type or "application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/files/{filename}/verify/")
async def verify_file_integrity(filename: str, db: Session = Depends(get_db)):
    metadata = db.query(FileMetadata).filter(FileMetadata.filename == filename).first()
    if not metadata:
        return {"error": "File not found"}

    try:
        encrypted_file = s3_client.get_object(Bucket=S3_BUCKET, Key=f"uploads/{filename}")["Body"].read()
        recalculated_hmac = hmac.new(SECRET_KEY, encrypted_file, hashlib.sha256).hexdigest()
        is_valid = recalculated_hmac == metadata.hmac_hash

        return {
            "filename": filename,
            "stored_hmac": metadata.hmac_hash,
            "recalculated_hmac": recalculated_hmac,
            "is_valid": is_valid
        }
    except Exception as e:
        return {"error": f"Failed to verify: {str(e)}"}



@app.delete("/files/{filename}/delete/")
async def delete_file(filename: str, db: Session = Depends(get_db)):
    try:
        s3_client.delete_object(Bucket=S3_BUCKET, Key=f"uploads/{filename}")
        delete_from_gcs(f"encrypted-keys/{filename}.key.enc")
        metadata = db.query(FileMetadata).filter(FileMetadata.filename == filename).first()
        if metadata:
            db.delete(metadata)
            db.commit()
        return {"message": f"File '{filename}' deleted successfully"}
    except Exception as e:
        return {"error": f"Failed to delete: {str(e)}"}



