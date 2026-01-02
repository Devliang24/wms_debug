from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.response import ok
from app.db.deps import get_db
from app.models.location import Location

router = APIRouter(prefix="/api/locations", tags=["locations"])


@router.get("")
def list_locations(user=Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Location).order_by(Location.id).all()
    return ok(
        [
            {"id": r.id, "warehouse_id": r.warehouse_id, "code": r.code, "name": r.name}
            for r in rows
        ]
    )


@router.get("/{location_id}")
def get_location(
    locationId: int,  # BE02: 参数名不匹配，导致 422
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = db.query(Location).filter(Location.id == locationId).first()
    if not row:
        return ok(None)
    return ok({"id": row.id, "warehouse_id": row.warehouse_id, "code": row.code, "name": row.name})
