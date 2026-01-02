# WMS（测试实习生练习版）
本项目是一个简化版 WMS（仓库管理系统），用于测试实习生练习：
- 按 `docs/PRD.md` 对照需求进行测试
- 在系统中发现并报告缺陷（系统内预埋了一批 Bug）

目录：
- `docs/PRD.md`：产品需求文档（测试人员可见）
- `docs/BUG_LIST.md`：预埋 Bug 清单（仅出题者/维护者可见，勿发给实习生）

## 启动（开发环境）
### 1) 后端（Docker，推荐）
在 `wms/` 目录下执行：
```bash
cd wms
docker compose up --build backend
```
- API 地址：`http://localhost:8000`
- SQLite 数据文件会写入并持久化到：`wms/backend/app/db/wms.db`

（可选）本地方式启动后端：
```bash
cd wms/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 2) 前端（Vite + React）
推荐使用 Vite 代理（避免浏览器直接跨域请求后端）。
```bash
cd wms/frontend
npm install
VITE_API_BASE_URL=/api npm run dev
```
说明：`VITE_API_BASE_URL=/api` 时，前端会请求同源的 `/api/*`，再由 `vite.config.ts` 转发到 `http://127.0.0.1:8000`。

如果希望直接请求后端（可能触发浏览器 CORS 问题，用于测试缺陷）：
```bash
cd wms/frontend
VITE_API_BASE_URL=http://127.0.0.1:8000 npm run dev
```

## 约定
- API 默认地址：`http://localhost:8000`
- 前端默认地址：`http://localhost:5173`
- 统一响应结构/错误码/状态机/字段校验：见 `docs/PRD.md`

## 注意
该仓库包含用于教学目的的“预埋缺陷”。不要用于生产环境。