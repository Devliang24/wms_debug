import { Button, Card, Form, Input, Modal, Space, Table, Tag, message } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useEffect, useMemo, useState } from 'react'

import { api } from '../services/api'

type Product = {
  id: number
  sku: string
  name: string
  category?: string | null
  unit?: string | null
  created_at?: string | null
}

type ListResp = {
  code: string
  message: string
  data: {
    items: Product[]
    total: number
    page: number
    page_size: number
    total_pages: number
  }
}

export default function ProductsPage() {
  const [q, setQ] = useState('')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<Product[]>([])
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState<number>(NaN)

  const [reloadNonce, setReloadNonce] = useState(0)

  const [createOpen, setCreateOpen] = useState(false)
  const [createForm] = Form.useForm()

  const [editOpen, setEditOpen] = useState(false)
  const [editForm] = Form.useForm()
  const [editing, setEditing] = useState<Product | null>(null)

  const columns: ColumnsType<Product> = useMemo(
    () => [
      { title: 'ID', dataIndex: 'id', width: 80 },
      { title: 'SKU', dataIndex: 'sku', width: 160 },
      {
        title: '名称',
        dataIndex: 'name',
        // FE16: XSS（错误：直接用 innerHTML 渲染商品名称）
        render: (v) => <span dangerouslySetInnerHTML={{ __html: String(v ?? '') }} />,
      },
      {
        title: '分类',
        dataIndex: 'category',
        width: 120,
        render: (v) => (v ? <Tag>{v}</Tag> : '-'),
      },
      { title: '单位', dataIndex: 'unit', width: 100 },
      { title: '创建时间', dataIndex: 'created_at', width: 220 },
      {
        title: '操作',
        width: 180,
        render: (_: any, row) => (
          <Space>
            <Button
              size="small"
              onClick={() => {
                setEditing(row)
                editForm.setFieldsValue(row)
                setEditOpen(true)
              }}
            >
              编辑
            </Button>
            <Button
              size="small"
              danger
              onClick={async () => {
                try {
                  await api.delete(`/api/products/${row.id}`)
                  message.success('删除成功')
                  setReloadNonce((n) => n + 1)
                } catch (e: any) {
                  message.error(e?.response?.data?.message || '删除失败')
                }
              }}
            >
              删除
            </Button>
          </Space>
        ),
      },
    ],
    [editForm],
  )

  useEffect(() => {
    let cancelled = false

    ;(async () => {
      setLoading(true)
      try {
        const resp = await api.get<ListResp>('/api/products', {
          params: {
            q: q || undefined,
            page,
            page_size: pageSize,
          },
        })
        if (cancelled) return
        setData(resp.data.data.items)
        setTotal(resp.data.data.total)
        // FE04: 读取错误字段导致总页数 NaN
        setTotalPages(Math.ceil(resp.data.data.total / Number((resp.data.data as any).pageSize)))
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()

    return () => {
      cancelled = true
    }
  }, [q, page, pageSize, reloadNonce])

  return (
    <Card
      title="商品管理"
      extra={
        <Space>
          <span>总页数：{String(totalPages)}</span>
          <Button
            type="primary"
            onClick={() => {
              createForm.resetFields()
              setCreateOpen(true)
            }}
          >
            新增商品
          </Button>
        </Space>
      }
    >
      <Space style={{ marginBottom: 12 }}>
        <Input
          placeholder="按名称/SKU 搜索"
          value={q}
          onChange={(e) => {
            setQ(e.target.value)
            setPage(1)
          }}
          style={{ width: 260 }}
        />
        <Button onClick={() => setQ('')}>清空</Button>
      </Space>

      <Table
        rowKey="id"
        loading={loading}
        columns={columns}
        dataSource={data}
        pagination={{
          current: page,
          pageSize,
          total,
          onChange: (p, ps) => {
            setPage(p)
            setPageSize(ps)
          },
        }}
      />

      <Modal
        title="新增商品"
        open={createOpen}
        onCancel={() => setCreateOpen(false)}
        onOk={() => createForm.submit()}
        okText="提交"
      >
        <Form
          form={createForm}
          layout="vertical"
          onFinish={async (values) => {
            try {
              await api.post('/api/products', values)
              message.success('创建成功')
              setCreateOpen(false)
              setReloadNonce((n) => n + 1)
            } catch (e: any) {
              message.error(e?.response?.data?.message || '创建失败')
            }
          }}
        >
          <Form.Item name="sku" label="SKU" rules={[{ required: true }]}
          >
            <Input />
          </Form.Item>
          <Form.Item name="name" label="名称" rules={[{ required: true }]}
          >
            <Input />
          </Form.Item>
          <Form.Item name="category" label="分类">
            <Input />
          </Form.Item>
          <Form.Item name="unit" label="单位">
            <Input />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={`编辑商品 ${editing?.sku || ''}`}
        open={editOpen}
        onCancel={() => setEditOpen(false)}
        onOk={() => editForm.submit()}
        okText="保存"
      >
        <Form
          form={editForm}
          layout="vertical"
          onFinish={async (values) => {
            if (!editing) return
            try {
              await api.put(`/api/products/${editing.id}`, values)
              message.success('保存成功')
              setEditOpen(false)
              // FE13: 编辑成功后不刷新列表，仍显示旧数据
            } catch (e: any) {
              message.error(e?.response?.data?.message || '保存失败')
            }
          }}
        >
          <Form.Item name="name" label="名称" rules={[{ required: true }]}
          >
            <Input />
          </Form.Item>
          <Form.Item name="category" label="分类">
            <Input />
          </Form.Item>
          <Form.Item name="unit" label="单位">
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}
