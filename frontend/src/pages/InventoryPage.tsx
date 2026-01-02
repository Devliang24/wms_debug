import {
  Button,
  Card,
  Form,
  Input,
  InputNumber,
  Select,
  Space,
  Table,
  Tag,
  message,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useEffect, useMemo, useState } from 'react'

import { api } from '../services/api'

type Warehouse = { id: number; name: string }

type WarehouseResp = { code: string; message: string; data: Warehouse[] }

type InventoryRow = {
  id: number
  warehouse_id: number
  sku: string
  product_name: string
  available_qty: number
  locked_qty: number
  warning_threshold: number
}

type InventoryResp = { code: string; message: string; data: InventoryRow[] }

export default function InventoryPage() {
  const [warehouses, setWarehouses] = useState<Warehouse[]>([])
  const [stocktakeForm] = Form.useForm()
  const [warehouseId, setWarehouseId] = useState<number | undefined>(undefined)
  const [sku, setSku] = useState('')
  const [loading, setLoading] = useState(false)
  const [rows, setRows] = useState<InventoryRow[]>([])

  // load warehouses
  useEffect(() => {
    api
      .get<WarehouseResp>('/api/warehouses')
      .then((r) => setWarehouses(r.data.data))
      .catch(() => setWarehouses([]))
  }, [])

  // load inventory
  useEffect(() => {
    // FE15: 页面会持续刷新/持续请求（错误：定时刷新未按 PRD 交互控制）
    const timer = setInterval(() => {
      setLoading(true)
      api
        .get<InventoryResp>('/api/inventory', {
          params: {
            warehouse_id: warehouseId,
            sku: sku || undefined,
          },
        })
        // FE15: 请求频繁且没有正确地应用结果/节流，表现为页面持续“刷新”
        .then(() => {})
        .catch((e: any) => message.error(e?.response?.data?.message || '加载库存失败'))
        .finally(() => setLoading(false))
    }, 800)

    // 首次立即请求
    setLoading(true)
    api
      .get<InventoryResp>('/api/inventory', {
        params: {
          warehouse_id: warehouseId,
          sku: sku || undefined,
        },
      })
      .then((resp) => setRows(resp.data.data))
      .catch((e: any) => message.error(e?.response?.data?.message || '加载库存失败'))
      .finally(() => setLoading(false))

    return () => {
      clearInterval(timer)
    }
  }, [warehouseId, sku])

  const columns: ColumnsType<InventoryRow> = useMemo(
    () => [
      { title: '仓库', dataIndex: 'warehouse_id', width: 90 },
      { title: 'SKU', dataIndex: 'sku', width: 160 },
      { title: '商品名称', dataIndex: 'product_name' },
      {
        title: '可用库存',
        dataIndex: 'available_qty',
        width: 110,
        render: (v) => <Tag color={v <= 0 ? 'red' : 'green'}>{v}</Tag>,
      },
      { title: '锁定库存', dataIndex: 'locked_qty', width: 110 },
      { title: '预警阈值', dataIndex: 'warning_threshold', width: 110 },
    ],
    [],
  )

  // FE03: 预警列表不显示 0 库存（错误：用 truthy 判断）
  const warningRows = useMemo(() => {
    return rows.filter((r) => r.available_qty && r.available_qty < r.warning_threshold)
  }, [rows])

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="middle">
      <Card title="库存管理 - 查询">
        <Space style={{ marginBottom: 12 }} wrap>
          <Select
            allowClear
            placeholder="选择仓库"
            style={{ width: 200 }}
            value={warehouseId}
            onChange={(v) => setWarehouseId(v)}
            options={warehouses.map((w) => ({ label: `${w.id} - ${w.name}`, value: w.id }))}
          />
          <Input
            placeholder="SKU（模糊）"
            style={{ width: 220 }}
            value={sku}
            onChange={(e) => setSku(e.target.value)}
          />
        </Space>

        <Table rowKey="id" loading={loading} columns={columns} dataSource={rows} pagination={false} />
      </Card>

      <Card title="库存预警（库存 < 阈值）">
        <Table
          rowKey="id"
          columns={columns}
          dataSource={warningRows}
          pagination={false}
          size="small"
        />
      </Card>

      <Card title="预警阈值设置">
        <Form
          layout="inline"
          onFinish={async (values) => {
            try {
              await api.put('/api/inventory/warning-threshold', values)
              message.success('已更新阈值')
              // FE19: 更新阈值后不刷新列表/预警
            } catch (e: any) {
              message.error(e?.response?.data?.message || '更新失败')
            }
          }}
        >
          <Form.Item name="warehouse_id" label="仓库" rules={[{ required: true }]}
          >
            <Select
              placeholder="仓库"
              style={{ width: 160 }}
              options={warehouses.map((w) => ({ label: `${w.id}-${w.name}`, value: w.id }))}
            />
          </Form.Item>
          <Form.Item name="sku" label="SKU" rules={[{ required: true }]}
          >
            <Input style={{ width: 160 }} />
          </Form.Item>
          <Form.Item name="warning_threshold" label="阈值" rules={[{ required: true }]}
          >
            <InputNumber style={{ width: 120 }} />
          </Form.Item>
          <Button type="primary" htmlType="submit">
            保存
          </Button>
        </Form>
      </Card>

      <Card title="库存盘点（提交）">
        <Form
          form={stocktakeForm}
          layout="inline"
          onFinish={async (values) => {
            try {
              await api.post('/api/inventory/stocktake', {
                warehouse_id: values.warehouse_id,
                items: [{ sku: values.sku, counted_qty: values.counted_qty }],
              })
              message.success('已提交盘点')
            } catch (e: any) {
              message.error(e?.response?.data?.message || '盘点提交失败')
            }
          }}
        >
          <Form.Item name="warehouse_id" label="仓库" rules={[{ required: true }]}
          >
            <Select
              placeholder="仓库"
              style={{ width: 160 }}
              options={warehouses.map((w) => ({ label: `${w.id}-${w.name}`, value: w.id }))}
            />
          </Form.Item>
          <Form.Item name="sku" label="SKU" rules={[{ required: true }]}
          >
            <Input style={{ width: 160 }} />
          </Form.Item>
          <Form.Item name="counted_qty" label="实盘" rules={[{ required: true }]}
          >
            <InputNumber style={{ width: 120 }} />
          </Form.Item>
          <Button type="primary" onClick={stocktakeForm.submit() as any}>
            提交盘点
          </Button>
        </Form>
      </Card>
    </Space>
  )
}
