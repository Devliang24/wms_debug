import { Navigate, Route, Routes } from 'react-router-dom'
import { BrowserRouter } from 'react-router-dom'

import AppLayout from './layout/AppLayout'
import NotFoundPage from './pages/NotFoundPage'
import LoginPage from './pages/LoginPage'
import ProductsPage from './pages/ProductsPage'
import WarehousesPage from './pages/WarehousesPage'
import InventoryPage from './pages/InventoryPage'
import InboundPage from './pages/InboundPage'
import InboundDetailPage from './pages/InboundDetailPage'
import OutboundPage from './pages/OutboundPage'
import LocationsPage from './pages/LocationsPage'
import AdminUsersPage from './pages/AdminUsersPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route path="/" element={<AppLayout />}>
          <Route index element={<Navigate to="/products" replace />} />
          <Route path="products" element={<ProductsPage />} />
          <Route path="inventory" element={<InventoryPage />} />
          <Route path="inbound" element={<InboundPage />} />
          <Route path="inbound/:id" element={<InboundDetailPage />} />
          <Route path="outbound" element={<OutboundPage />} />
          <Route path="warehouses" element={<WarehousesPage />} />
          <Route path="locations" element={<LocationsPage />} />
          <Route path="admin/users" element={<AdminUsersPage />} />
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  )
}
