from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.inventory import Inventory
from app.models.location import Location
from app.models.product import Product
from app.models.user import User
from app.models.warehouse import Warehouse


def init_db(db: Session) -> None:
    # Warehouses
    if db.query(Warehouse).count() == 0:
        db.add_all([
            Warehouse(id=1, name="WH-A"),
            Warehouse(id=2, name="WH-B"),
        ])
        db.commit()

    # Locations
    if db.query(Location).count() == 0:
        db.add_all([
            Location(warehouse_id=1, code="A-01", name="A区01"),
            Location(warehouse_id=2, code="B-01", name="B区01"),
        ])
        db.commit()

    # Users
    if db.query(User).count() == 0:
        db.add_all([
            User(username="admin", password_hash=get_password_hash("admin123"), role="admin", warehouse_ids="1,2"),
            User(username="op_a", password_hash=get_password_hash("op123"), role="operator", warehouse_ids="1"),
            User(username="op_b", password_hash=get_password_hash("op123"), role="operator", warehouse_ids="2"),
        ])
        db.commit()

    # Products
    if db.query(Product).count() == 0:
        p1 = Product(sku="SKU-001", name="测试商品1", category="默认", unit="pcs")
        p2 = Product(sku="SKU-002", name="测试商品2", category="默认", unit="pcs")
        p3 = Product(sku="SKU-003", name="测试商品3", category="默认", unit="pcs")
        db.add_all([p1, p2, p3])
        db.commit()

    # Inventory
    if db.query(Inventory).count() == 0:
        products = db.query(Product).all()
        items = []
        for p in products:
            items.append(Inventory(warehouse_id=1, product_id=p.id, available_qty=50, locked_qty=0, warning_threshold=10))
            items.append(Inventory(warehouse_id=2, product_id=p.id, available_qty=20, locked_qty=0, warning_threshold=5))
        db.add_all(items)
        db.commit()
