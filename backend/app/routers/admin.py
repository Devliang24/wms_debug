from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.response import ok
from app.db.deps import get_db
from app.models.user import User

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
def list_users(user=Depends(get_current_user), db: Session = Depends(get_db)):
    # BE20: 缺少管理员角色校验（operator 也能访问）
    rows = db.query(User).order_by(User.id).all()
    return ok(
        [
            {
                "id": u.id,
                "username": u.username,
                "role": u.role,
                "warehouse_ids": u.warehouse_ids,
            }
            for u in rows
        ]
    )
