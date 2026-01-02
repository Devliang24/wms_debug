from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.db.session import Base


class InboundOrder(Base):
    __tablename__ = "inbound_orders"

    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="PENDING")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    confirmed_at = Column(DateTime, nullable=True)


class InboundOrderItem(Base):
    __tablename__ = "inbound_order_items"

    id = Column(Integer, primary_key=True, index=True)
    inbound_order_id = Column(Integer, ForeignKey("inbound_orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)

    sku = Column(String(32), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False, default=0)  # 简化：单位分
