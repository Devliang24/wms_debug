from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.db.session import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(32), nullable=False, index=True)  # 按计划：不加唯一约束（BE11 可重复）
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)
    unit = Column(String(20), nullable=True)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
