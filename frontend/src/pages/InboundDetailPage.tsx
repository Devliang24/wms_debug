import { Button, Card, Descriptions, Space, Table, message } from 'antd'
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'

import { api } from '../services/api'

type InboundItem = { sku: string; quantity: number; unit_price: number }

type InboundDetail = {
  id: number
  warehouse_id: number
  status: string
  created_at?: string | null
  confirmed_at?: string | null
  items: InboundItem[]
}

type Resp = { code: string; message: string; data: InboundDetail }

export default function InboundDetailPage() {
  const params = useParams()
  const id = Number(params.id)

  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<InboundDetail | null>(null)

  const load = async () => {
    setLoading(true)
    try {
      const resp = await api.get<Resp>(`/api/inbound/${id}`)
      setData(resp.data.data)
    } catch (e: any) {
      message.error(e?.response?.data?.message || '加载失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!Number.isFinite(id)) return
    load()
  }, [id])

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="middle">
      <Card
        title={`入库单详情 #${id}`}
        extra={
          <Space>
            <Button
              onClick={async () => {
                try {
                  await api.put(`/api/inbound/${id}/confirm`)
                  message.success('已确认入库')
                  load()
                } catch (e: any) {
                  message.error(e?.response?.data?.message || '确认失败')
                }
              }}
            >
              确认入库
            </Button>
            <Button onClick={load} loading={loading}>
              刷新
            </Button>
          </Space>
        }
      >
        <Descriptions bordered size="small" column={2}>
          <Descriptions.Item label="ID">{data?.id ?? '-'}</Descriptions.Item>
          <Descriptions.Item label="仓库">{data?.warehouse_id ?? '-'}</Descriptions.Item>
          <Descriptions.Item label="状态">{data?.status ?? '-'}</Descriptions.Item>
          <Descriptions.Item label="创建时间">{data?.created_at ?? '-'}</Descriptions.Item>
          <Descriptions.Item label="确认时间">{data?.confirmed_at ?? '-'}</Descriptions.Item>
        </Descriptions>

        <div style={{ marginTop: 12 }}>
          <Table
            rowKey={(r) => r.sku}
            size="small"
            pagination={false}
            dataSource={data?.items || []}
            columns={[
              { title: 'SKU', dataIndex: 'sku' },
              { title: '数量', dataIndex: 'quantity', width: 120 },
              { title: '单价', dataIndex: 'unit_price', width: 120 },
            ]}
          />
        </div>
      </Card>
    </Space>
  )
}
