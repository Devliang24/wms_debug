import { Button, Card, Form, Input, Select, Space, Table, Typography, message } from 'antd'
import { Link } from 'react-router-dom'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'
import { useEffect, useMemo, useState } from 'react'

import { api } from '../services/api'

type Warehouse = { id: number; name: string }

type WarehouseResp = { code: string; message: string; data: Warehouse[] }

type InboundOrder = {
  id: number
  warehouse_id: number
  status: string
  created_at?: string | null
  confirmed_at?: string | null
}

type InboundListResp = { code: string; message: string; data: InboundOrder[] }

type InboundItem = { sku: string; quantity: any; unit_price: any }

export default function InboundPage() {
  const [warehouses, setWarehouses] = useState<Warehouse[]>([])
  const [warehouseId, setWarehouseId] = useState<number | undefined>(undefined)
  const [list, setList] = useState<InboundOrder[]>([])
  const [loading, setLoading] = useState(false)

  const [items, setItems] = useState<InboundItem[]>([{ sku: 'SKU-001', quantity: '1', unit_price: '9.9' }])
  const [totalQty, setTotalQty] = useState<any>(0)
  const [totalAmount, setTotalAmount] = useState<number>(0)

  const recalcTotals = (nextItems: InboundItem[]) => {
    // FE10: quantity 为 string，直接相加导致字符串拼接
    const qty = nextItems.reduce((acc: any, it) => acc + it.quantity, 0)
    // FE14: 金额精度问题（浮点运算）
    const amount = nextItems.reduce(
      (acc: number, it) => acc + Number(it.quantity) * Number(it.unit_price),
      0,
    )
    setTotalQty(qty)
    setTotalAmount(amount)
  }

  useEffect(() => {
    api
      .get<WarehouseResp>('/api/warehouses')
      .then((r) => setWarehouses(r.data.data))
      .catch(() => setWarehouses([]))

    // init totals
    recalcTotals(items)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // FE01: 仓库切换不刷新（缺少 warehouseId 依赖）
  useEffect(() => {
    let cancelled = false
    ;(async () => {
      setLoading(true)
      try {
        const resp = await api.get<InboundListResp>('/api/inbound', {
          params: {
            warehouse_id: warehouseId,
          },
        })
        if (!cancelled) setList(resp.data.data)
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()

    return () => {
      cancelled = true
    }
  }, [])

  const columns: ColumnsType<InboundOrder> = useMemo(
    () => [
      {
        title: 'ID',
        dataIndex: 'id',
        width: 80,
        render: (v) => <Link to={`/inbound/${v}`}>{v}</Link>,
      },
      { title: '仓库', dataIndex: 'warehouse_id', width: 90 },
      { title: '状态', dataIndex: 'status', width: 120 },
      {
        title: '创建时间',
        dataIndex: 'created_at',
        width: 200,
        render: (v) => dayjs(v).format('YYYY-MM-DD HH:mm:ss'),
      },
      {
        title: '确认时间',
        dataIndex: 'confirmed_at',
        width: 200,
        // FE05: confirmed_at 为空时显示 Invalid Date
        render: (v) => dayjs(v).format('YYYY-MM-DD HH:mm:ss'),
      },
    ],
    [],
  )


  return (
    <Space direction="vertical" style={{ width: '100%' }} size="middle">
      <Card title="入库管理 - 入库单列表">
        <Space style={{ marginBottom: 12 }}>
          <Select
            allowClear
            placeholder="选择仓库"
            style={{ width: 200 }}
            value={warehouseId}
            onChange={(v) => setWarehouseId(v)}
            options={warehouses.map((w) => ({ label: `${w.id}-${w.name}`, value: w.id }))}
          />
        </Space>

        <Table rowKey="id" loading={loading} columns={columns} dataSource={list} pagination={false} />
      </Card>

      <Card title="创建入库单">
        <Form
          layout="vertical"
          onFinish={async (values) => {
            try {
              await api.post('/api/inbound', {
                warehouse_id: values.warehouse_id,
                items,
              })
              message.success('创建成功')
              // FE12: 不做 loading 禁用，快速点击可重复提交产生重复单据
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
                render: (_: any, row: InboundItem, idx: number) => (
                  <Input
                    value={row.sku}
                    onChange={(e) => {
                      const next = items.slice()
                      next[idx] = { ...next[idx], sku: e.target.value }
                      setItems(next)
                      recalcTotals(next)
                    }}
                  />
                ),
              },
              {
                title: '数量',
                dataIndex: 'quantity',
                width: 120,
                render: (_: any, row: InboundItem, idx: number) => (
                  <Input
                    value={row.quantity}
                    onChange={(e) => {
                      const next = items.slice()
                      next[idx] = { ...next[idx], quantity: e.target.value }
                      setItems(next)
                      recalcTotals(next)
                    }}
                  />
                ),
              },
              {
                title: '单价(元)',
                dataIndex: 'unit_price',
                width: 160,
                render: (_: any, row: InboundItem, idx: number) => (
                  <Input
                    value={row.unit_price}
                    onChange={(e) => {
                      const next = items.slice()
                      next[idx] = { ...next[idx], unit_price: e.target.value }
                      setItems(next)
                      recalcTotals(next)
                    }}
                  />
                ),
              },
              {
                title: '操作',
                width: 90,
                render: (_: any, __: InboundItem, idx: number) => (
                  <Button
                    danger
                    onClick={() => {
                      const next = items.filter((_, i) => i !== idx)
                      setItems(next)
                      // FE20: 删除行后总数不更新（故意不 recalcTotals）
                    }}
                  >
                    删除
                  </Button>
                ),
              },
            ]}
          />

          <Space style={{ marginTop: 12 }}>
            <Button
              onClick={() => {
                const next = [...items, { sku: '', quantity: '1', unit_price: '0' }]
                setItems(next)
                recalcTotals(next)
              }}
            >
              添加行
            </Button>
          </Space>

          <div style={{ marginTop: 12 }}>
            <Typography.Text>总数量：{String(totalQty)}</Typography.Text>
            <br />
            <Typography.Text>总金额：{String(totalAmount)}</Typography.Text>
          </div>

          <Button type="primary" htmlType="submit" style={{ marginTop: 12 }}>
            提交创建
          </Button>
        </Form>
      </Card>
    </Space>
  )
}
