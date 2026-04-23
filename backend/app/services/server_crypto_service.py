import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings


class ServerCryptoService:
    def __init__(self) -> None:
        key = base64.b64decode(settings.file_encryption_key_base64)
        if len(key) not in (16, 24, 32):
            raise ValueError("file_encryption_key_base64 é invalida")
        self._key = key
        self._aesgcm = AESGCM(self._key)

    def encrypt_bytes(self, plain_data: bytes) -> tuple[bytes, str, str]:
        nonce = os.urandom(12)
        encrypted = self._aesgcm.encrypt(nonce, plain_data, None)
        return encrypted, "AES-256-GCM", base64.b64encode(nonce).decode("ascii")

    def decrypt_bytes(self, encrypted_data: bytes, nonce_base64: str) -> bytes:
        nonce = base64.b64decode(nonce_base64)
        return self._aesgcm.decrypt(nonce, encrypted_data, None)
