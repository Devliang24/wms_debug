from fastapi import APIRouter

from app.core.response import ok

router = APIRouter(prefix="/api")


@router.get("/health")
def health():
    # BE03: 不符合统一响应格式
    return {"status": "ok"}
