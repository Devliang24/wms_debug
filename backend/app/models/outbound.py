from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.db.session import Base


class OutboundOrder(Base):
    __tablename__ = "outbound_orders"

    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="PENDING_PICK")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    picked_at = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)


class OutboundOrderItem(Base):
    __tablename__ = "outbound_order_items"

    id = Column(Integer, primary_key=True, index=True)
    outbound_order_id = Column(Integer, ForeignKey("outbound_orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)

    sku = Column(String(32), nullable=False)
    quantity = Column(Integer, nullable=False)
