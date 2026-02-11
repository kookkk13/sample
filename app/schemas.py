from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Any | None = None


class LoginRequest(BaseModel):
    baseUrl: str | None = Field(default=None, min_length=1)
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    success: bool = True


class VirtualCenterItem(BaseModel):
    id: str | None = None
    name: str | None = None
    fqdn: str | None = None
    status: str | None = None
    version: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class VirtualCentersResponse(BaseModel):
    items: list[VirtualCenterItem]
