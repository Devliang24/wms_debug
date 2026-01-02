import { Card, List } from 'antd'
import { useEffect, useState } from 'react'

import { api } from '../services/api'

type Warehouse = { id: number; name: string }

type Resp = { code: string; message: string; data: Warehouse[] }

export default function WarehousesPage() {
  const [data, setData] = useState<Warehouse[]>([])

  useEffect(() => {
    api
      .get<Resp>('/api/warehouses')
      .then((r) => setData(r.data.data))
      .catch(() => setData([]))
  }, [])

  return (
    <Card title="仓库设置">
      <List
        bordered
        dataSource={data}
        renderItem={(item) => <List.Item>{item.id} - {item.name}</List.Item>}
      />
    </Card>
  )
}
