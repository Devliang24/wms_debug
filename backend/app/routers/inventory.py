from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.response import ok
from app.db.deps import get_db
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.stocktake import Stocktake, StocktakeItem
from app.models.warehouse import Warehouse
from app.schemas.inventory import StocktakeSubmitRequest, TransferRequest, WarningThresholdUpdate

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


@router.get("")
def list_inventory(
    warehouse_id: Optional[int] = None,
    sku: Optional[str] = None,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # BE16: sku 过滤使用字符串拼接 SQL（SQL 注入风险）
    if sku:
        sql = text(
            f"""
            SELECT i.id, i.warehouse_id, i.product_id, i.available_qty, i.locked_qty, i.warning_threshold,
                   p.sku as sku, p.name as product_name
            FROM inventory i
            JOIN products p ON p.id = i.product_id
            WHERE p.sku LIKE '%{sku}%'
            """
        )
        rows = db.execute(sql).mappings().all()
        return ok([dict(r) for r in rows])

    q = db.query(Inventory, Product).join(Product, Product.id == Inventory.product_id)
    if warehouse_id is not None:
        q = q.filter(Inventory.warehouse_id == warehouse_id)

    rows = q.all()
    out: List[Dict[str, Any]] = []
    for inv, p in rows:
        out.append(
            {
                "id": inv.id,
                "warehouse_id": inv.warehouse_id,
                "sku": p.sku,
                "product_name": p.name,
                "available_qty": inv.available_qty,
                "locked_qty": inv.locked_qty,
                "warning_threshold": inv.warning_threshold,
            }
        )
    return ok(out)


@router.put("/warning-threshold")
def update_warning_threshold(
    payload: WarningThresholdUpdate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    p = db.query(Product).filter(Product.sku == payload.sku).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": "product not found"})

    inv = (
        db.query(Inventory)
        .filter(Inventory.warehouse_id == payload.warehouse_id)
        .filter(Inventory.product_id == p.id)
        .first()
    )
    if not inv:
        inv = Inventory(warehouse_id=payload.warehouse_id, product_id=p.id, available_qty=0, locked_qty=0)
        db.add(inv)
        db.commit()
        db.refresh(inv)

    inv.warning_threshold = payload.warning_threshold
    db.commit()
    return ok(True)


@router.post("/transfer")
def transfer_inventory(
    payload: TransferRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.quantity <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"code": "VALIDATION_ERROR", "message": "quantity must be >0"})

    p = db.query(Product).filter(Product.sku == payload.sku).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": "product not found"})

    src = (
        db.query(Inventory)
        .filter(Inventory.warehouse_id == payload.from_warehouse_id)
        .filter(Inventory.product_id == p.id)
        .first()
    )
    if not src or (src.available_qty or 0) < payload.quantity:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"code": "INSUFFICIENT_STOCK", "message": "insufficient stock"})

    # BE10: 非原子 —— 先扣源仓并 commit，再做目标仓（若后续报错会导致数据不一致）
    src.available_qty = (src.available_qty or 0) - payload.quantity
    db.commit()

    # 故意把目标仓存在性校验放在 commit 之后
    dst_wh = db.query(Warehouse).filter(Warehouse.id == payload.to_warehouse_id).first()
    if not dst_wh:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": "destination warehouse not found"})

    dst = (
        db.query(Inventory)
        .filter(Inventory.warehouse_id == payload.to_warehouse_id)
        .filter(Inventory.product_id == p.id)
        .first()
    )
    if not dst:
        dst = Inventory(warehouse_id=payload.to_warehouse_id, product_id=p.id, available_qty=0, locked_qty=0)
        db.add(dst)
        db.commit()
        db.refresh(dst)

    dst.available_qty = (dst.available_qty or 0) + payload.quantity
    db.commit()

    # BE18: 缺少审计日志（不写入 InventoryAuditLog）
    return ok(True)


@router.post("/stocktake")
def submit_stocktake(
    payload: StocktakeSubmitRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # BE22: 允许重复提交（不校验 status）
    if payload.stocktake_id is not None:
        st = db.query(Stocktake).filter(Stocktake.id == payload.stocktake_id).first()
        if not st:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": "stocktake not found"})
    else:
        st = Stocktake(warehouse_id=payload.warehouse_id, status="SUBMITTED")
        db.add(st)
        db.commit()
        db.refresh(st)

    # 保存盘点明细（简化：每次提交都追加 item）
    for it in payload.items:
        p = db.query(Product).filter(Product.sku == it.sku).first()
        if not p:
            continue
        db.add(StocktakeItem(stocktake_id=st.id, product_id=p.id, sku=it.sku, counted_qty=it.counted_qty))

        inv = (
            db.query(Inventory)
            .filter(Inventory.warehouse_id == payload.warehouse_id)
            .filter(Inventory.product_id == p.id)
            .first()
        )
        if not inv:
            inv = Inventory(warehouse_id=payload.warehouse_id, product_id=p.id, available_qty=0, locked_qty=0)
            db.add(inv)
            db.commit()
            db.refresh(inv)

        # 简化：盘点直接覆盖可用库存
        inv.available_qty = it.counted_qty

    db.commit()
    return ok({"stocktake_id": st.id, "status": st.status})
