from google.cloud import storage
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get bucket name from .env
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

def upload_to_gcs(object_name: str, data: bytes):
    """
    Uploads the given byte data to a Google Cloud Storage bucket.

    Args:
    - object_name: Path/filename in the bucket (e.g., "encrypted-keys/file1.key.enc")
    - data: Byte content to upload (e.g., an encrypted AES key)
    """
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)
    blob.upload_from_string(data)

def download_from_gcs(object_name: str) -> bytes:
    """
    Downloads a file (as bytes) from a GCS bucket.

    Args:
    - object_name: Path/filename in the bucket

    Returns:
    - The byte content of the downloaded file (e.g., encrypted AES key)
    """
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)
    return blob.download_as_bytes()
