from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.response import ok
from app.db.deps import get_db
from app.models.warehouse import Warehouse

router = APIRouter(prefix="/api/warehouses", tags=["warehouses"])


@router.get("")
def list_warehouses(user=Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Warehouse).order_by(Warehouse.id).all()
    return ok([{"id": w.id, "name": w.name} for w in rows])
