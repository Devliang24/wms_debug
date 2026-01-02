import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.jwt import create_access_token
from app.core.response import ok
from app.core.security import verify_password
from app.db.deps import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # BE15: 敏感信息泄露（日志打印明文密码）
    logger.warning("login attempt user=%s password=%s", payload.username, payload.password)

    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "invalid username or password"},
        )

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return ok(
        {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "warehouse_ids": user.warehouse_ids,
            },
        }
    )


@router.post("/logout")
def logout():
    # 简化：JWT 无状态，前端自行丢弃 token
    return ok(True)


@router.post("/refresh")
def refresh():
    # 简化：不实现 refresh token
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail={"code": "NOT_IMPLEMENTED", "message": "not implemented"})
