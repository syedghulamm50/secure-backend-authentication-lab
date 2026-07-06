import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Generate a 256-bit key for AES (In production, save this in a .env file)
# Example: KEY = AESGCM.generate_key(bit_length=256)
SECRET_KEY = b'sixteen_byte_key_sixteen_byte_k' # Must be exactly 32 bytes for AES-256

def encrypt_data(plaintext: str) -> bytes:
    """Encrypts plaintext using AES-256-GCM."""
    aesgcm = AESGCM(SECRET_KEY)
    nonce = os.urandom(12)  # Unique Initialization Vector (IV) for every encryption
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    return nonce + ciphertext  # Prepend nonce so we can extract it during decryption

def decrypt_data(ciphertext_with_nonce: bytes) -> str:
    """Decrypts ciphertext using AES-256-GCM."""
    aesgcm = AESGCM(SECRET_KEY)
    nonce = ciphertext_with_nonce[:12]
    ciphertext = ciphertext_with_nonce[12:]
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode()
