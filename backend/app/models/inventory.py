from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer

from app.db.session import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)

    available_qty = Column(Integer, nullable=False, default=0)
    locked_qty = Column(Integer, nullable=False, default=0)

    warning_threshold = Column(Integer, nullable=False, default=0)

    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
