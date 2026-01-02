from typing import Any, Dict

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def _wrap_error(code: str, message: str, data: Any = None) -> Dict[str, Any]:
    return {"code": code, "message": message, "data": data}


def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    # 兼容: detail 可能是 str 或 dict
    if isinstance(exc.detail, dict) and "code" in exc.detail and "message" in exc.detail:
        body = _wrap_error(str(exc.detail.get("code")), str(exc.detail.get("message")), exc.detail.get("data"))
    else:
        body = _wrap_error("ERROR", str(exc.detail), None)
    return JSONResponse(status_code=exc.status_code, content=body)


def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=_wrap_error("VALIDATION_ERROR", "validation error", exc.errors()),
    )
