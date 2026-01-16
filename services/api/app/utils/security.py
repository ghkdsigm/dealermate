from datetime import datetime, timedelta
from typing import Any

"""
Compatibility shim:
passlib==1.7.4 expects bcrypt.__about__.__version__, but bcrypt>=4 removed __about__.
This crashes app startup on modern environments (e.g. Python 3.12).
"""
try:
    import types
    import bcrypt as _bcrypt  # type: ignore

    if not hasattr(_bcrypt, "__about__"):
        _bcrypt.__about__ = types.SimpleNamespace(  # type: ignore[attr-defined]
            __version__=getattr(_bcrypt, "__version__", "unknown")
        )
except Exception:
    # If bcrypt isn't installed (or any unexpected import-time issue), let passlib raise a clearer error later.
    pass

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Default to pbkdf2_sha256 to avoid bcrypt's 72-byte password limit (which can crash startup seeding).
# Keep bcrypt* in the list so we can still verify existing hashes if any were created previously.
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt_sha256", "bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_access_token(subject: str, role: str, branch_id: str, expires_minutes: int = 60 * 12) -> str:
    now = datetime.utcnow()
    payload: dict[str, Any] = {
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "sub": subject,
        "role": role,
        "branch_id": branch_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"], audience=settings.jwt_audience, issuer=settings.jwt_issuer)
