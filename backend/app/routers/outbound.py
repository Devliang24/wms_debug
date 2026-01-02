from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.response import ok
from app.core.timefmt import fmt
from app.db.deps import get_db
from app.models.inventory import Inventory
from app.models.outbound import OutboundOrder, OutboundOrderItem
from app.models.product import Product
from app.schemas.outbound import OutboundCreateRequest

router = APIRouter(prefix="/api/outbound", tags=["outbound"])


@router.get("")
def list_outbound(
    warehouse_id: Optional[int] = None,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(OutboundOrder)
    if warehouse_id is not None:
        q = q.filter(OutboundOrder.warehouse_id == warehouse_id)

    orders = q.order_by(OutboundOrder.id.desc()).all()

    # BE17: N+1 查询 —— 每个订单单独查询 items
    out: List[Dict[str, Any]] = []
    for o in orders:
        items = db.query(OutboundOrderItem).filter(OutboundOrderItem.outbound_order_id == o.id).all()
        out.append(
            {
                "id": o.id,
                "warehouse_id": o.warehouse_id,
                "status": o.status,
                "created_at": fmt(o.created_at),
                "picked_at": fmt(o.picked_at),
                "shipped_at": fmt(o.shipped_at),
                "items": [
                    {"sku": it.sku, "quantity": it.quantity, "product_id": it.product_id} for it in items
                ],
            }
        )

    return ok(out)


@router.post("")
def create_outbound(
    payload: OutboundCreateRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = OutboundOrder(warehouse_id=payload.warehouse_id, status="PENDING_PICK", created_by=user.id)
    db.add(order)
    db.commit()
    db.refresh(order)

    for it in payload.items:
        p = db.query(Product).filter(Product.sku == it.sku).first()
        if not p:
            continue
        # BE12: 不校验库存是否充足
        db.add(OutboundOrderItem(outbound_order_id=order.id, product_id=p.id, sku=it.sku, quantity=it.quantity))
    db.commit()

    return ok({"id": order.id, "warehouse_id": order.warehouse_id, "status": order.status})


@router.put("/{outbound_id}/pick")
def pick_outbound(
    outbound_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(OutboundOrder).filter(OutboundOrder.id == outbound_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": "outbound not found"})

    # BE14: 不校验状态
    order.status = "PICKED"
    db.commit()
    return ok(True)


@router.delete("/{outbound_id}")
def delete_outbound(
    outbound_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(OutboundOrder).filter(OutboundOrder.id == outbound_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "outbound not found"},
        )

    db.query(OutboundOrderItem).filter(OutboundOrderItem.outbound_order_id == order.id).delete()
    db.delete(order)
    db.commit()
    return ok(True)


@router.put("/{outbound_id}/ship")
def ship_outbound(
    outbound_id: int,
    simulate_fail: bool = Query(default=False),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(OutboundOrder).filter(OutboundOrder.id == outbound_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": "outbound not found"})

    items = db.query(OutboundOrderItem).filter(OutboundOrderItem.outbound_order_id == order.id).all()

    if simulate_fail:
        # BE08: 先扣库存并提交，再失败（不回滚）
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
            if inv:
                inv.available_qty = (inv.available_qty or 0) - (it.quantity or 0)
        db.commit()

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"code": "SHIP_FAILED", "message": "carrier error"})

    # BE07: 发货成功但不扣减库存
    order.status = "SHIPPED"
    db.commit()
    return ok(True)
