import { Button, Card, Form, Input, Modal, Select, Space, Table, Typography, message } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import type { Key } from 'react'
import { useCallback, useEffect, useMemo, useState } from 'react'

import { api } from '../services/api'

type Warehouse = { id: number; name: string }

type WarehouseResp = { code: string; message: string; data: Warehouse[] }

type OutboundItem = { sku: string; quantity: any }

type OutboundOrder = {
  id: number
  warehouse_id: number
  status: string
  created_at?: string | null
  items?: { sku: string; quantity: number }[]
}

type OutboundListResp = { code: string; message: string; data: OutboundOrder[] }

export default function OutboundPage() {
  const [warehouses, setWarehouses] = useState<Warehouse[]>([])
  const [warehouseId, setWarehouseId] = useState<number | undefined>(undefined)
  const [list, setList] = useState<OutboundOrder[]>([])
  const [loading, setLoading] = useState(false)

  const [items, setItems] = useState<OutboundItem[]>([{ sku: 'SKU-001', quantity: '1' }])
  const [selectedRowKeys, setSelectedRowKeys] = useState<Key[]>([])
  const [batchResults, setBatchResults] = useState<string[]>([])

  const [pickOpen, setPickOpen] = useState(false)
  const [pickOrderId, setPickOrderId] = useState<number | null>(null)
  const [pickSku, setPickSku] = useState('')

  useEffect(() => {
    api
      .get<WarehouseResp>('/api/warehouses')
      .then((r) => setWarehouses(r.data.data))
      .catch(() => setWarehouses([]))
  }, [])

  const loadList = async () => {
    setLoading(true)
    try {
      const resp = await api.get<OutboundListResp>('/api/outbound', {
        params: { warehouse_id: warehouseId },
      })
      setList(resp.data.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadList()
  }, [warehouseId])

  // FE07: useCallback 依赖缺失导致闭包旧值（pickSku 不在依赖）
  const confirmPick = useCallback(async () => {
    if (!pickOrderId) return
    await api.put(`/api/outbound/${pickOrderId}/pick`, { scanned_sku: pickSku })
    message.success(`已拣货（SKU=${pickSku}）`)
    setPickOpen(false)
    loadList()
  }, [pickOrderId])

  const columns: ColumnsType<OutboundOrder> = useMemo(
    () => [
      { title: 'ID', dataIndex: 'id', width: 80 },
      { title: '仓库', dataIndex: 'warehouse_id', width: 90 },
      { title: '状态', dataIndex: 'status', width: 140 },
      {
        title: '明细',
        dataIndex: 'items',
        render: (items?: any[]) => (
          <span>
            {(items || []).map((it) => `${it.sku}×${it.quantity}`).join('，')}
          </span>
        ),
      },
      {
        title: '操作',
        width: 240,
        render: (_: any, row) => (
          <Space>
            <Button
              size="small"
              onClick={() => {
                setPickOrderId(row.id)
                setPickSku('')
                setPickOpen(true)
              }}
            >
              拣货
            </Button>
            <Button
              size="small"
              type="primary"
              onClick={async () => {
                await api.put(`/api/outbound/${row.id}/ship`)
                message.success('已发货')
                loadList()
              }}
            >
              发货
            </Button>
            <Button
              size="small"
              danger
              onClick={async () => {
                await api.delete(`/api/outbound/${row.id}`)
                message.success('删除成功')
                // FE11: 删除成功后不刷新列表
              }}
            >
              删除
            </Button>
          </Space>
        ),
      },
    ],
    [warehouseId],
  )

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="middle">
      <Card title="出库管理 - 出库单列表">
        <Space style={{ marginBottom: 12 }}>
          <Select
            allowClear
            placeholder="选择仓库"
            style={{ width: 200 }}
            value={warehouseId}
            onChange={(v) => setWarehouseId(v)}
            options={warehouses.map((w) => ({ label: `${w.id}-${w.name}`, value: w.id }))}
          />
          <Button
            onClick={async () => {
              // FE08: 批量发货状态展示错乱：并发 setState 覆盖（非函数式更新）
              setBatchResults([])
              await Promise.all(
                selectedRowKeys.map(async (id) => {
                  try {
                    await api.put(`/api/outbound/${id}/ship`)
                    setBatchResults([...batchResults, `#${id}: ok`])
                  } catch {
                    setBatchResults([...batchResults, `#${id}: fail`])
                  }
                }),
              )
              loadList()
            }}
          >
            批量发货
          </Button>
        </Space>

        {batchResults.length > 0 && (
          <div style={{ marginBottom: 12 }}>
            <Typography.Text>批量结果：</Typography.Text>
            <div>{batchResults.join(' | ')}</div>
          </div>
        )}

        <Table
          rowKey="id"
          loading={loading}
          columns={columns}
          dataSource={list}
          rowSelection={{
            selectedRowKeys,
            onChange: (keys) => setSelectedRowKeys(keys),
          }}
          pagination={false}
        />
      </Card>

      <Modal
        title={`拣货确认 #${pickOrderId ?? ''}`}
        open={pickOpen}
        onCancel={() => setPickOpen(false)}
        onOk={confirmPick}
        okText="确认拣货"
      >
        <div style={{ marginBottom: 8 }}>扫描/输入 SKU：</div>
        <Input value={pickSku} onChange={(e) => setPickSku(e.target.value)} placeholder="SKU" />
      </Modal>

      <Card title="创建出库单">
        <Form
          layout="vertical"
          onFinish={async (values) => {
            try {
              // FE18: 前端不校验库存是否充足
              await api.post('/api/outbound', {
                warehouse_id: values.warehouse_id,
                items,
              })
              message.success('创建成功')
              loadList()
            } catch (e: any) {
              message.error(e?.response?.data?.message || '创建失败')
            }
          }}
        >
          <Form.Item name="warehouse_id" label="仓库" rules={[{ required: true }]}
          >
            <Select
              placeholder="选择仓库"
              options={warehouses.map((w) => ({ label: `${w.id}-${w.name}`, value: w.id }))}
            />
          </Form.Item>

          <Table
            rowKey={(_, idx) => String(idx)}
            dataSource={items}
            pagination={false}
            size="small"
            columns={[
              {
                title: 'SKU',
                dataIndex: 'sku',
                render: (_: any, row: OutboundItem, idx: number) => (
                  <Input
                    value={row.sku}
                    onChange={(e) => {
                      const next = items.slice()
                      next[idx] = { ...next[idx], sku: e.target.value }
                      setItems(next)
                    }}
                  />
                ),
              },
              {
                title: '数量',
                dataIndex: 'quantity',
                width: 120,
                render: (_: any, row: OutboundItem, idx: number) => (
                  <Input
                    value={row.quantity}
                    onChange={(e) => {
                      const next = items.slice()
                      next[idx] = { ...next[idx], quantity: e.target.value }
                      setItems(next)
                    }}
                  />
                ),
              },
              {
                title: '操作',
                width: 90,
                render: (_: any, __: OutboundItem, idx: number) => (
                  <Button
                    danger
                    onClick={() => {
                      setItems(items.filter((_, i) => i !== idx))
                    }}
                  >
                    删除
                  </Button>
                ),
              },
            ]}
          />

          <Space style={{ marginTop: 12 }}>
            <Button onClick={() => setItems([...items, { sku: '', quantity: '1' }])}>添加行</Button>
          </Space>

          <Button type="primary" htmlType="submit" style={{ marginTop: 12 }}>
            提交创建
          </Button>
        </Form>
      </Card>
    </Space>
  )
}
