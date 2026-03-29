from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

from .config import get_settings

PASSWORD_SCHEME = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 310_000
ACCESS_TOKEN_TTL_HOURS = 12


@dataclass
class AccessTokenPayload:
    user_id: str
    tenant_id: str
    login_name: str
    expires_at: int


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(raw: str) -> bytes:
    padding = "=" * (-len(raw) % 4)
    return base64.urlsafe_b64decode(f"{raw}{padding}")


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)
    return "$".join(
        [
            PASSWORD_SCHEME,
            str(PASSWORD_ITERATIONS),
            _b64url_encode(salt),
            _b64url_encode(derived),
        ]
    )


def verify_password(password: str, password_hash: str) -> bool:
    try:
        scheme, iterations_raw, salt_raw, digest_raw = password_hash.split("$", 3)
    except ValueError:
        return False

    if scheme != PASSWORD_SCHEME:
        return False

    iterations = int(iterations_raw)
    salt = _b64url_decode(salt_raw)
    expected = _b64url_decode(digest_raw)
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(actual, expected)


def create_access_token(user_id: str, tenant_id: str, login_name: str) -> str:
    settings = get_settings()
    expires_at = int((datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_TTL_HOURS)).timestamp())
    payload = {
        "sub": user_id,
        "tenantId": tenant_id,
        "loginName": login_name,
        "exp": expires_at,
    }
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = hmac.new(settings.jwt_secret.encode("utf-8"), payload_bytes, hashlib.sha256).digest()
    return f"{_b64url_encode(payload_bytes)}.{_b64url_encode(signature)}"


def decode_access_token(token: str) -> AccessTokenPayload:
    settings = get_settings()

    try:
        payload_raw, signature_raw = token.split(".", 1)
        payload_bytes = _b64url_decode(payload_raw)
        expected_signature = hmac.new(settings.jwt_secret.encode("utf-8"), payload_bytes, hashlib.sha256).digest()
        actual_signature = _b64url_decode(signature_raw)
    except Exception as exc:  # pragma: no cover - defensive path
        raise HTTPException(status_code=401, detail="无效的访问令牌") from exc

    if not hmac.compare_digest(expected_signature, actual_signature):
        raise HTTPException(status_code=401, detail="访问令牌签名无效")

    payload = json.loads(payload_bytes.decode("utf-8"))
    expires_at = int(payload.get("exp", 0))
    if expires_at <= int(datetime.now(timezone.utc).timestamp()):
        raise HTTPException(status_code=401, detail="访问令牌已过期")

    return AccessTokenPayload(
        user_id=str(payload["sub"]),
        tenant_id=str(payload["tenantId"]),
        login_name=str(payload["loginName"]),
        expires_at=expires_at,
    )
