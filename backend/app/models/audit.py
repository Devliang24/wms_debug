from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.db.session import Base


class InventoryAuditLog(Base):
    __tablename__ = "inventory_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, nullable=True, index=True)
    operator_id = Column(Integer, nullable=True, index=True)

    action = Column(String(50), nullable=False)  # e.g. TRANSFER/INBOUND/OUTBOUND/STOCKTAKE
    sku = Column(String(32), nullable=True)

    old_qty = Column(Integer, nullable=True)
    new_qty = Column(Integer, nullable=True)
    delta = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
