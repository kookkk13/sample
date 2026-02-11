from __future__ import annotations

import logging
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import Header

from app.config import get_settings
from app.errors import AppError
from app.vcf_client import VCFClient

logger = logging.getLogger(__name__)


@dataclass
class SessionData:
    vcf_token: str
    expires_at: datetime


class SessionStore:
    def __init__(self) -> None:
        self._store: dict[str, SessionData] = {}
        self.settings = get_settings()

    def create(self, vcf_token: str) -> tuple[str, int]:
        ttl = self.settings.session_ttl_seconds
        session_token = secrets.token_urlsafe(32)
        self._store[session_token] = SessionData(vcf_token=vcf_token, expires_at=datetime.now(timezone.utc) + timedelta(seconds=ttl))
        return session_token, ttl

    def get(self, session_token: str) -> SessionData | None:
        session = self._store.get(session_token)
        if not session:
            return None

        if datetime.now(timezone.utc) >= session.expires_at:
            self._store.pop(session_token, None)
            return None

        return session

    def invalidate(self, session_token: str) -> None:
        self._store.pop(session_token, None)


def mask_secret(value: str) -> str:
    if len(value) <= 4:
        return "****"
    return f"{value[:2]}***{value[-2:]}"


vcf_client = VCFClient()
session_store = SessionStore()


async def login_vcf(username: str, password: str) -> tuple[str, int]:
    logger.info("VCF login attempt username=%s password=%s", username, mask_secret(password))
    vcf_token = await vcf_client.login_vcf(username=username, password=password)
    session_token, ttl = session_store.create(vcf_token)
    logger.info("VCF login successful username=%s session=%s", username, mask_secret(session_token))
    return session_token, ttl


async def require_session_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AppError(status_code=401, code="AUTH_REQUIRED", message="Missing Bearer token")

    session_token = authorization.split(" ", 1)[1].strip()
    session_data = session_store.get(session_token)
    if not session_data:
        raise AppError(status_code=401, code="INVALID_SESSION", message="Invalid or expired session")

    return session_data.vcf_token
