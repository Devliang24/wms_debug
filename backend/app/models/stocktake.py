from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.db.session import Base


class Stocktake(Base):
    __tablename__ = "stocktakes"

    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="DRAFT")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    submitted_at = Column(DateTime, nullable=True)


class StocktakeItem(Base):
    __tablename__ = "stocktake_items"

    id = Column(Integer, primary_key=True, index=True)
    stocktake_id = Column(Integer, ForeignKey("stocktakes.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    sku = Column(String(32), nullable=False)
    counted_qty = Column(Integer, nullable=False)
