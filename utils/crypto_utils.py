from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def encrypt_file(content: bytes) -> tuple[bytes, bytes, bytes]:
    """
    Encrypts the given file content using AES-GCM.

    Returns:
    - encrypted_file: The encrypted bytes (nonce + tag + ciphertext)
    - key: The randomly generated AES key
    - nonce: The random nonce used during encryption (can be stored or used for decryption)
    """
    key = get_random_bytes(32)  # AES-256 key (32 bytes)
    cipher = AES.new(key, AES.MODE_GCM)  # AES in GCM mode for authenticated encryption
    ciphertext, tag = cipher.encrypt_and_digest(content)  # Encrypt and get tag for integrity

    # Concatenate nonce + tag + ciphertext for easier storage/retrieval
    encrypted_file = cipher.nonce + tag + ciphertext
    return encrypted_file, key, cipher.nonce


def decrypt_file(encrypted_file: bytes, key: bytes) -> bytes:
    """
    Decrypts an AES-GCM encrypted file.

    Args:
    - encrypted_file: The encrypted file bytes (nonce + tag + ciphertext)
    - key: The AES key used during encryption (must match original)

    Returns:
    - Decrypted plaintext bytes
    """
    nonce = encrypted_file[:16]         # AES-GCM nonce is 16 bytes
    tag = encrypted_file[16:32]         # Authentication tag is 16 bytes
    ciphertext = encrypted_file[32:]    # The rest is the encrypted content

    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext
