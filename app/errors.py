from fastapi import Request
from fastapi.responses import JSONResponse

from app.schemas import ErrorResponse


class AppError(Exception):
    def __init__(self, *, status_code: int, code: str, message: str, details: dict | None = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    payload = ErrorResponse(code=exc.code, message=exc.message, details=exc.details)
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
    payload = ErrorResponse(code="INTERNAL_ERROR", message="An unexpected error occurred", details={"type": type(exc).__name__})
    return JSONResponse(status_code=500, content=payload.model_dump())
