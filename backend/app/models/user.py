from sqlalchemy import Column, Integer, String

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="operator")
    # 简化：用逗号分隔的仓库 ID 列表，例如 "1,2"
    warehouse_ids = Column(String(100), nullable=True)
