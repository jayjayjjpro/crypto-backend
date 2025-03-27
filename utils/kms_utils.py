from google.cloud import kms
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get values from .env
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_KMS_LOCATION")
KEY_RING = os.getenv("GCP_KMS_KEY_RING")
KEY_NAME = os.getenv("GCP_KMS_KEY_NAME")

# Initialize KMS client
client = kms.KeyManagementServiceClient()
key_path = client.crypto_key_path(PROJECT_ID, LOCATION, KEY_RING, KEY_NAME)

def encrypt_key_with_kms(plaintext: bytes) -> bytes:
    """
    Encrypt a key using Google Cloud KMS.
    """
    response = client.encrypt(request={"name": key_path, "plaintext": plaintext})
    return response.ciphertext

def decrypt_key_with_kms(ciphertext: bytes) -> bytes:
    """
    Decrypt a key using Google Cloud KMS.
    """
    response = client.decrypt(request={"name": key_path, "ciphertext": ciphertext})
    return response.plaintext
