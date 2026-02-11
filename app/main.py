import logging

from fastapi import Depends, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.auth import SessionData, login_vcf, require_session_token
from app.config import get_settings
from app.errors import AppError, app_error_handler, unhandled_error_handler
from app.schemas import LoginRequest, LoginResponse, VirtualCenterItem, VirtualCentersResponse
from app.vcf_client import vcf_client

settings = get_settings()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/login", response_model=LoginResponse)
async def login(payload: LoginRequest, response: Response) -> LoginResponse:
    session_token, expires_in = await login_vcf(payload.username, payload.password, payload.baseUrl)
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=expires_in,
    )
    return LoginResponse(success=True)


@app.get("/api/virtualcenters", response_model=VirtualCentersResponse)
async def virtual_centers(session: SessionData = Depends(require_session_token)) -> VirtualCentersResponse:
    raw_items = await vcf_client.get_virtual_centers(token=session.vcf_token, base_url=session.base_url)

    items = [
        VirtualCenterItem(
            id=item.get("id") or item.get("uuid"),
            name=item.get("name"),
            fqdn=item.get("fqdn") or item.get("hostname"),
            status=item.get("status") or item.get("health"),
            version=item.get("version") or item.get("build"),
            raw=item,
        )
        for item in raw_items
    ]
    return VirtualCentersResponse(items=items)
