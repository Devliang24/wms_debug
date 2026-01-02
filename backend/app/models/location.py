from sqlalchemy import Column, ForeignKey, Integer, String

from app.db.session import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    code = Column(String(50), nullable=False)
    name = Column(String(100), nullable=True)
