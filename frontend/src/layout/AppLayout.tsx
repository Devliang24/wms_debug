import { Layout, Menu } from 'antd'
import { Link, Outlet, useLocation } from 'react-router-dom'

const { Header, Sider, Content } = Layout

const items = [
  { key: '/products', label: <Link to="/products">商品管理</Link> },
  { key: '/inventory', label: <Link to="/inventory">库存管理</Link> },
  { key: '/inbound', label: <Link to="/inbound">入库管理</Link> },
  { key: '/outbound', label: <Link to="/outbound">出库管理</Link> },
  { key: '/warehouses', label: <Link to="/warehouses">仓库设置</Link> },
  { key: '/locations', label: <Link to="/locations">库位管理</Link> },
  { key: '/admin/users', label: <Link to="/admin/users">管理员-用户</Link> },
]

export default function AppLayout() {
  const location = useLocation()

  const selectedKey = location.pathname.startsWith('/admin')
    ? '/admin/users'
    : `/${location.pathname.split('/')[1]}`

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider breakpoint="lg" collapsedWidth={56}>
        <div className="px-3 py-4 text-white font-semibold">WMS</div>
        <Menu theme="dark" mode="inline" selectedKeys={[selectedKey]} items={items} />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 16px' }}>
          <div className="flex items-center justify-between">
            <div className="font-semibold">WMS（测试实习生练习版）</div>
            <Link to="/login">登录</Link>
          </div>
        </Header>
        <Content style={{ padding: 16 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
