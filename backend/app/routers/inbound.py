from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.response import ok
from app.core.timefmt import fmt
from app.db.deps import get_db
from app.models.inbound import InboundOrder, InboundOrderItem
from app.models.inventory import Inventory
from app.models.product import Product
from app.schemas.inbound import InboundCreateRequest, InboundUpdateRequest

router = APIRouter(prefix="/api/inbound", tags=["inbound"])


@router.get("")
def list_inbound(
    warehouse_id: Optional[int] = None,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(InboundOrder)
    if warehouse_id is not None:
        q = q.filter(InboundOrder.warehouse_id == warehouse_id)

    rows = q.order_by(InboundOrder.id.desc()).all()
    return ok(
        [
            {
                "id": r.id,
                "warehouse_id": r.warehouse_id,
                "status": r.status,
                "created_at": fmt(r.created_at),
                "confirmed_at": fmt(r.confirmed_at),
            }
            for r in rows
        ]
    )


@router.post("")
def create_inbound(
    payload: InboundCreateRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = InboundOrder(warehouse_id=payload.warehouse_id, status="PENDING", created_by=user.id)
    db.add(order)
    db.commit()
    db.refresh(order)

    for it in payload.items:
        p = db.query(Product).filter(Product.sku == it.sku).first()
        if not p:
            continue
        # BE09: 不校验 quantity > 0
        db.add(
            InboundOrderItem(
                inbound_order_id=order.id,
                product_id=p.id,
                sku=it.sku,
                quantity=it.quantity,
                unit_price=int(it.unit_price * 100),
            )
        )
    db.commit()

    # BE01: 返回结构不符合统一 {code,message,data}
    return {"id": order.id, "warehouse_id": order.warehouse_id, "status": order.status, "created_at": order.created_at.isoformat()}


@router.get("/{inbound_id}")
def get_inbound(
    inbound_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(InboundOrder).filter(InboundOrder.id == inbound_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "inbound not found"},
        )

    items = db.query(InboundOrderItem).filter(InboundOrderItem.inbound_order_id == order.id).all()
    return ok(
        {
            "id": order.id,
            "warehouse_id": order.warehouse_id,
            "status": order.status,
            "created_at": fmt(order.created_at),
            "confirmed_at": fmt(order.confirmed_at),
            # FE17/BE21: 不校验是否属于当前用户授权仓库（越权可读）
            "items": [
                {
                    "sku": it.sku,
                    "quantity": it.quantity,
                    "unit_price": (it.unit_price or 0) / 100,
                }
                for it in items
            ],
        }
    )


@router.put("/{inbound_id}/confirm")
def confirm_inbound(
    inbound_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(InboundOrder).filter(InboundOrder.id == inbound_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": "inbound not found"})

    # BE14: 不校验状态，允许重复确认
    items = db.query(InboundOrderItem).filter(InboundOrderItem.inbound_order_id == order.id).all()
    for it in items:
        p = db.query(Product).filter(Product.id == it.product_id).first()
        if not p:
            continue
        inv = (
            db.query(Inventory)
            .filter(Inventory.warehouse_id == order.warehouse_id)
            .filter(Inventory.product_id == p.id)
            .first()
        )
        if not inv:
            inv = Inventory(warehouse_id=order.warehouse_id, product_id=p.id, available_qty=0, locked_qty=0)
            db.add(inv)
            db.commit()
            db.refresh(inv)
        inv.available_qty = (inv.available_qty or 0) + (it.quantity or 0)

    order.status = "CONFIRMED"
    db.commit()
    return ok(True)


@router.put("/{inbound_id}")
def update_inbound_items(
    inbound_id: int,
    payload: InboundUpdateRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(InboundOrder).filter(InboundOrder.id == inbound_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": "inbound not found"})

    # BE23: 已确认仍可修改（不校验 order.status）
    db.query(InboundOrderItem).filter(InboundOrderItem.inbound_order_id == order.id).delete()
    db.commit()

    for it in payload.items:
        p = db.query(Product).filter(Product.sku == it.sku).first()
        if not p:
            continue
        db.add(
            InboundOrderItem(
                inbound_order_id=order.id,
                product_id=p.id,
                sku=it.sku,
                quantity=it.quantity,
                unit_price=int(it.unit_price * 100),
            )
        )
    db.commit()

    return ok(True)
