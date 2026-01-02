import { Button, Card, Form, Input, message } from 'antd'
import { useNavigate } from 'react-router-dom'

import { api } from '../services/api'
import { setToken } from '../services/auth'

type LoginResp = {
  code: string
  message: string
  data: {
    access_token: string
    token_type: string
  }
}

export default function LoginPage() {
  const navigate = useNavigate()

  return (
    <div className="h-full flex items-center justify-center">
      <Card title="登录" style={{ width: 360 }}>
        <Form
          layout="vertical"
          onFinish={async (values) => {
            try {
              const resp = await api.post<LoginResp>('/api/auth/login', values)
              setToken(resp.data.data.access_token)
              message.success('登录成功')
              navigate('/products')
            } catch (e: any) {
              message.error(e?.response?.data?.message || '登录失败')
            }
          }}
        >
          <Form.Item name="username" label="用户名" rules={[{ required: true }]}>
            <Input placeholder="admin / op_a / op_b" />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true }]}>
            <Input.Password placeholder="admin123 / op123" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block>
            登录
          </Button>
        </Form>
      </Card>
    </div>
  )
}
