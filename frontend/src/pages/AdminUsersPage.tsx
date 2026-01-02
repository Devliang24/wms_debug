import { Card, Table } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useEffect, useMemo, useState } from 'react'

import { api } from '../services/api'

type UserRow = { id: number; username: string; role: string; warehouse_ids?: string | null }

type Resp = { code: string; message: string; data: UserRow[] }

export default function AdminUsersPage() {
  const [data, setData] = useState<UserRow[]>([])

  useEffect(() => {
    api
      .get<Resp>('/api/admin/users')
      .then((r) => setData(r.data.data))
      .catch(() => setData([]))
  }, [])

  const columns: ColumnsType<UserRow> = useMemo(
    () => [
      { title: 'ID', dataIndex: 'id', width: 80 },
      { title: '用户名', dataIndex: 'username', width: 160 },
      { title: '角色', dataIndex: 'role', width: 120 },
      { title: '仓库权限', dataIndex: 'warehouse_ids' },
    ],
    [],
  )

  return (
    <Card title="管理员 - 用户列表">
      <Table rowKey="id" columns={columns} dataSource={data} pagination={false} />
    </Card>
  )
}
