import { Button, Card, List, Modal, Space, message } from 'antd'
import { useEffect, useState } from 'react'

import { api } from '../services/api'

type Location = { id: number; warehouse_id: number; code: string; name?: string | null }

type ListResp = { code: string; message: string; data: Location[] }

type DetailResp = { code: string; message: string; data: Location | null }

export default function LocationsPage() {
  const [list, setList] = useState<Location[]>([])

  useEffect(() => {
    api
      .get<ListResp>('/api/locations')
      .then((r) => {
        // FE09: 切换页面过快，定时回写导致卸载后 setState 报错
        setTimeout(() => setList(r.data.data), 600)
      })
      .catch(() => setList([]))
  }, [])

  const showDetail = async (id: number) => {
    try {
      const resp = await api.get<DetailResp>(`/api/locations/${id}`)
      Modal.info({ title: '库位详情', content: <pre>{JSON.stringify(resp.data.data, null, 2)}</pre> })
    } catch (e: any) {
      message.error(e?.response?.data?.message || '获取库位详情失败')
    }
  }

  return (
    <Card title="库位管理">
      <List
        bordered
        dataSource={list}
        renderItem={(item) => (
          <List.Item
            actions={[
              <Button key="detail" size="small" onClick={() => showDetail(item.id)}>
                详情
              </Button>,
            ]}
          >
            <Space>
              <span>#{item.id}</span>
              <span>WH:{item.warehouse_id}</span>
              <span>{item.code}</span>
              <span>{item.name || '-'}</span>
            </Space>
          </List.Item>
        )}
      />
    </Card>
  )
}
