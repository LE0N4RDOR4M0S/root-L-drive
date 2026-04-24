import base64
import hashlib
import hmac
import json
import time

from fastapi import HTTPException, status

from app.core.config import settings


class PreviewProxyService:
    def __init__(self) -> None:
        self._secret = settings.jwt_secret_key.encode("utf-8")

    @staticmethod
    def _b64url_encode(raw: bytes) -> str:
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

    @staticmethod
    def _b64url_decode(value: str) -> bytes:
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode(f"{value}{padding}".encode("ascii"))

    def create_token(self, *, file_id: str, owner_id: str, expires_in_seconds: int = 900) -> str:
        payload = {
            "file_id": file_id,
            "owner_id": owner_id,
            "exp": int(time.time()) + max(60, expires_in_seconds),
            "purpose": "preview-proxy",
        }
        payload_raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        payload_part = self._b64url_encode(payload_raw)
        signature = hmac.new(self._secret, payload_part.encode("ascii"), hashlib.sha256).digest()
        return f"{payload_part}.{self._b64url_encode(signature)}"

    def verify_token(self, token: str) -> dict:
        try:
          payload_part, signature_part = token.split(".", 1)
        except ValueError as exc:
          raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid preview token") from exc

        expected_signature = hmac.new(self._secret, payload_part.encode("ascii"), hashlib.sha256).digest()
        provided_signature = self._b64url_decode(signature_part)

        if not hmac.compare_digest(expected_signature, provided_signature):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid preview token")

        try:
            payload = json.loads(self._b64url_decode(payload_part).decode("utf-8"))
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid preview token") from exc

        if payload.get("purpose") != "preview-proxy":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid preview token")

        exp = payload.get("exp")
        if not isinstance(exp, int) or exp < int(time.time()):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Preview token expired")

        file_id = payload.get("file_id")
        owner_id = payload.get("owner_id")
        if not isinstance(file_id, str) or not file_id or not isinstance(owner_id, str) or not owner_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid preview token")

        return payload