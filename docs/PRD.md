# WMS 产品需求文档（PRD）
版本: v0.1
更新时间: 2025-12-31
面向读者: 测试实习生、开发

## 1. 背景与目标
本系统为简化版 WMS（仓库管理系统），覆盖常见业务：商品、库存、入库、出库、仓库/库位。
测试实习生需要基于本 PRD 编写测试用例、执行测试并提交缺陷报告。

## 2. 角色与权限
- Admin（管理员）
  - 可访问管理接口（如用户/仓库配置等）
- Warehouse Operator（仓库操作员）
  - 仅可操作被授权仓库的数据（仓库数据隔离）

通用规则：
- 所有业务接口必须登录后访问
- 普通用户不可访问管理员接口

## 3. 通用约定（接口/数据/交互）
### 3.1 时间格式
所有接口返回时间字段统一为：`YYYY-MM-DD HH:mm:ss`

### 3.2 分页
- 默认：`page=1`，`page_size=20`
- 约束：`page >= 1`，`1 <= page_size <= 100`

### 3.3 统一响应结构
成功响应：
- HTTP 200/201
- Body：
```json
{ "code": "OK", "message": "ok", "data": {} }
```
失败响应（统一 body 结构）：
- 400 BAD_REQUEST：`code=BAD_REQUEST`
- 401 UNAUTHORIZED：`code=UNAUTHORIZED`
- 403 FORBIDDEN：`code=FORBIDDEN`
- 404 NOT_FOUND：`code=NOT_FOUND`
- 409 CONFLICT：业务冲突（库存不足/SKU 重复/状态冲突等）
- 422 VALIDATION_ERROR：字段校验失败

说明：如采用 FastAPI/Pydantic 默认 422 格式，需要在接口文档中明确；建议统一包装为上述结构以降低测试难度。

### 3.4 交互规范
- 表单提交时应禁用按钮防止重复提交
- 列表切换筛选条件后应立即刷新
- 编辑成功返回列表后应显示最新数据
- 删除成功后列表应立即移除该记录
- 中文输入（IME composing）过程中不应触发搜索请求

## 4. 功能模块需求
## 4.1 商品管理
功能需求：
- 商品列表
  - 支持分页（默认 20/页）
  - 支持按名称/SKU 搜索
  - 支持按分类筛选
- 新增商品
  - 字段：SKU（必填/唯一）、名称（必填）、规格、单位、分类、图片
- 编辑商品
  - 修改后列表应立即展示最新数据
- 删除商品
  - 有库存的商品不允许删除

业务规则与校验：
- SKU 必须全局唯一
- 商品名称长度 ≤ 100
- 图片格式仅 jpg/png/gif，大小 ≤ 5MB

验收点：
- 新增重复 SKU 返回 409（SKU_DUPLICATED）
- 有库存商品删除返回 409（PRODUCT_HAS_STOCK）

## 4.2 库存管理
功能需求：
- 库存列表
  - 按仓库、商品筛选
  - 显示：可用库存、锁定库存
- 库存预警
  - 显示库存低于阈值的商品（包含库存=0）
  - 阈值修改后应立即生效
- 库存调拨
  - 从 A 仓调拨到 B 仓
- 库存盘点
  - 创建盘点单、录入实盘数量、提交盘点

业务规则与校验：
- 库存不允许为负数
- 调拨必须保证源仓库存充足
- 调拨为原子操作：源仓扣减与目标仓增加必须同时成功或同时失败
- 盘点单只能提交一次，不可重复提交
- 所有库存变动必须记录审计日志（操作人、时间、类型、数量）

验收点：
- 调拨源仓库存不足返回 409（INSUFFICIENT_STOCK）
- 盘点重复提交返回 409（STOCKTAKE_ALREADY_SUBMITTED）

## 4.3 入库管理
功能需求：
- 入库单列表
  - 按仓库、状态、日期筛选
- 创建入库单
  - 选择仓库
  - 添加商品行（商品 + 数量 + 单价）
- 入库确认
  - 确认后库存增加

状态机：
- InboundOrder.status：`DRAFT | PENDING | CONFIRMED | CANCELED`
- 允许流转：
  - DRAFT -> PENDING（创建）
  - PENDING -> CONFIRMED（确认入库：PUT /api/inbound/:id/confirm）
  - DRAFT -> CANCELED（取消）
- 禁止：
  - CONFIRMED 不可修改/不可再次确认/不可删除

业务规则与校验：
- 入库数量必须为正整数（>0）
- 商品行删除/修改后，底部总数量/总金额应自动重算
- 金额计算精度：保留 2 位小数

验收点：
- 已入库单据再次确认返回 409（INBOUND_STATUS_CONFLICT）
- 已入库单据修改返回 409（INBOUND_STATUS_CONFLICT）

## 4.4 出库管理
功能需求：
- 出库单列表：按仓库、状态、日期筛选
- 创建出库单：选择仓库、添加商品行
- 拣货确认：标记拣货完成
- 发货确认：确认后扣减库存

状态机：
- OutboundOrder.status：`DRAFT | PENDING_PICK | PICKED | SHIPPED | CANCELED`
- 允许流转：
  - DRAFT -> PENDING_PICK（创建）
  - PENDING_PICK -> PICKED（拣货：PUT /api/outbound/:id/pick）
  - PICKED -> SHIPPED（发货：PUT /api/outbound/:id/ship）
- 禁止：
  - SHIPPED 不可回退，不可修改数量

业务规则与校验：
- 创建/发货时必须校验库存充足，不得超卖
- 出库数量不能超过可用库存
- 发货失败需回滚库存

验收点：
- 库存不足返回 409（INSUFFICIENT_STOCK）

## 4.5 仓库设置
功能需求：
- 仓库列表
- 库位列表/详情

业务规则：
- 仓库人员仅能操作授权仓库的数据

## 5. 字段校验示例（用于测试断言）
### 5.1 创建商品 POST /api/products
- sku: string，必填，1-32，建议正则 `^[A-Z0-9-]+$`，唯一
- name: string，必填，1-100
- category: string，可选，<=50
- unit: string，可选，<=20
- image: file，可选，jpg/png/gif，<=5MB

### 5.2 创建出库单 POST /api/outbound
- warehouse_id: int，必填
- items[].sku: string，必填
- items[].quantity: int，必填，>0
- 若库存不足：返回 409（INSUFFICIENT_STOCK）

## 6. API 列表
- 认证
  - POST /api/auth/login
  - POST /api/auth/logout
  - POST /api/auth/refresh
- 商品
  - GET/POST /api/products
  - GET/PUT/DELETE /api/products/:id
- 库存
  - GET /api/inventory
  - POST /api/inventory/transfer
  - POST /api/inventory/stocktake
- 入库
  - GET/POST /api/inbound
  - PUT /api/inbound/:id/confirm
- 出库
  - GET/POST /api/outbound
  - PUT /api/outbound/:id/pick
  - PUT /api/outbound/:id/ship
- 仓库/库位
  - GET /api/warehouses
  - GET /api/locations
  - GET /api/locations/:id
