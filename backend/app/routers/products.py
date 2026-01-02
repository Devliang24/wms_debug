import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.response import ok
from app.core.timefmt import fmt
from app.db.deps import get_db
from app.models.inventory import Inventory
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("")
def list_products(
    q: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    order_by: str = "id",  # BE13: 未白名单校验，非法字段可能导致 500
    db: Session = Depends(get_db),
):
    # BE19: 列表接口未鉴权（按 PRD 应登录后访问）
    query = db.query(Product)
    if q:
        query = query.filter(or_(Product.name.contains(q), Product.sku.contains(q)))
    if category:
        query = query.filter(Product.category == category)

    # order_by 未校验
    query = query.order_by(getattr(Product, order_by))

    total = query.count()
    # BE04: page_size=0 会导致除零异常
    total_pages = math.ceil(total / page_size)
    rows = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for p in rows:
        # BE06: 这里返回 ISO 时间；其他接口可能返回 YYYY-MM-DD HH:mm:ss
        items.append(
            {
                "id": p.id,
                "sku": p.sku,
                "name": p.name,
                "category": p.category,
                "unit": p.unit,
                "image_url": p.image_url,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
        )

    return ok({"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages})


@router.post("")
def create_product(
    payload: ProductCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # BE11: 不校验 SKU 唯一
    p = Product(
        sku=payload.sku,
        name=payload.name,
        category=payload.category,
        unit=payload.unit,
        image_url=payload.image_url,
    )
    db.add(p)
    db.commit()
    db.refresh(p)

    return ok(
        {
            "id": p.id,
            "sku": p.sku,
            "name": p.name,
            "category": p.category,
            "unit": p.unit,
            "image_url": p.image_url,
            "created_at": fmt(p.created_at),
        }
    )


@router.get("/{product_id}")
def get_product(
    product_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": "product not found"})

    return ok(
        {
            "id": p.id,
            "sku": p.sku,
            "name": p.name,
            "category": p.category,
            "unit": p.unit,
            "image_url": p.image_url,
            "created_at": fmt(p.created_at),
        }
    )


@router.put("/{product_id}")
def update_product(
    product_id: int,
    payload: ProductUpdate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": "product not found"})

    if payload.name is not None:
        p.name = payload.name
    if payload.category is not None:
        p.category = payload.category
    if payload.unit is not None:
        p.unit = payload.unit
    if payload.image_url is not None:
        p.image_url = payload.image_url

    db.commit()
    return ok(True)


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": "product not found"})

    inv_rows = db.query(Inventory).filter(Inventory.product_id == p.id).all()
    qty_sum = sum((r.available_qty or 0) + (r.locked_qty or 0) for r in inv_rows)
    if qty_sum > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"code": "PRODUCT_HAS_STOCK", "message": "product has stock"})

    db.delete(p)
    # BE05: 缺少 commit，返回成功但实际未删除
    return ok(True)
