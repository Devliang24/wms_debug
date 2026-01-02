from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exception_handlers import http_exception_handler, validation_exception_handler
from app.db.init_db import init_db
from app.db.session import Base, SessionLocal, engine
from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.inbound import router as inbound_router
from app.routers.inventory import router as inventory_router
from app.routers.locations import router as locations_router
from app.routers.outbound import router as outbound_router
from app.routers.products import router as products_router
from app.routers.warehouses import router as warehouses_router

# 关键：导入 models 以注册 ORM 映射（后续会补齐）
# noqa: F401
try:
    import app.models  # type: ignore
except Exception:
    pass

# 简化：开发环境直接 create_all（无需 Alembic）
Base.metadata.create_all(bind=engine)

app = FastAPI(title="WMS API", version="0.1.0")

# 统一异常响应（符合 PRD），但仍会保留部分“预埋缺陷”
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# CORS middleware configuration (BE03 fixed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup_seed_data() -> None:
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(products_router)
app.include_router(warehouses_router)
app.include_router(locations_router)
app.include_router(inventory_router)
app.include_router(inbound_router)
app.include_router(outbound_router)
app.include_router(admin_router)
