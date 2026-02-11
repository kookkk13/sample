from __future__ import annotations

import logging
from collections.abc import Mapping

import httpx

from app.config import get_settings
from app.errors import AppError

logger = logging.getLogger(__name__)


class VCFClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def _request_with_retry(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        json: dict | None = None,
    ) -> httpx.Response:
        last_exc: Exception | None = None
        timeout = httpx.Timeout(self.settings.vcf_timeout_seconds)

        for attempt in range(self.settings.vcf_retry_count + 1):
            try:
                async with httpx.AsyncClient(
                    base_url=self.settings.vcf_base_url,
                    timeout=timeout,
                    verify=self.settings.vcf_verify_ssl,
                ) as client:
                    response = await client.request(method, path, headers=headers, json=json)
                    return response
            except httpx.RequestError as exc:
                last_exc = exc
                logger.warning("VCF request failed on attempt %s/%s: %s", attempt + 1, self.settings.vcf_retry_count + 1, exc)

        raise AppError(
            status_code=502,
            code="VCF_UNAVAILABLE",
            message="Failed to communicate with VCF API",
            details={"error": str(last_exc)} if last_exc else None,
        )

    async def login_vcf(self, username: str, password: str) -> str:
        response = await self._request_with_retry(
            "POST",
            "/api/session",
            json={"username": username, "password": password},
        )

        if response.status_code == 401:
            raise AppError(status_code=401, code="INVALID_CREDENTIALS", message="Invalid VCF credentials")

        if response.status_code >= 400:
            raise AppError(
                status_code=502,
                code="VCF_LOGIN_FAILED",
                message="VCF login failed",
                details={"status_code": response.status_code, "body": response.text[:300]},
            )

        token = response.headers.get("x-vmware-vcloud-access-token")
        if not token:
            body = response.json() if "application/json" in response.headers.get("content-type", "") else {}
            token = body.get("token") if isinstance(body, dict) else None

        if not token:
            raise AppError(status_code=502, code="VCF_TOKEN_MISSING", message="VCF token not found in response")

        return token

    async def get_virtual_centers(self, token: str) -> list[dict]:
        response = await self._request_with_retry(
            "GET",
            "/v1/virtual-centers",
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code == 401:
            raise AppError(status_code=401, code="VCF_TOKEN_EXPIRED", message="VCF token expired or invalid")

        if response.status_code >= 400:
            raise AppError(
                status_code=502,
                code="VCF_FETCH_FAILED",
                message="Failed to fetch virtual centers from VCF",
                details={"status_code": response.status_code, "body": response.text[:300]},
            )

        data = response.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and isinstance(data.get("elements"), list):
            return data["elements"]
        if isinstance(data, dict) and isinstance(data.get("items"), list):
            return data["items"]

        raise AppError(status_code=502, code="VCF_BAD_RESPONSE", message="Unexpected response format from VCF")

vcf_client = VCFClient()
