import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import Login from './pages/Login'
import Register from './pages/Register'
import UserHomePage from './pages/UserHomePage'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import Resale from './pages/Resale'
import LaptopPrediction from './pages/LaptopPrediction'
import SmartphonePrediction from './pages/SmartphonePrediction'
import SmartProductFinder from './pages/SmartProductFinder'
import CreateListing from './pages/CreateListing'
import Marketplace from './pages/Marketplace'
import ProductDetails from './pages/ProductDetails'
import Messages from './pages/Messages'

// Admin imports
import ErrorBoundary from './components/ErrorBoundary'
import ProtectedAdminRoute from './components/admin/ProtectedAdminRoute'
import AdminLayout from './pages/admin/AdminLayout'
import AdminDashboard from './pages/admin/AdminDashboard'
import UserManagement from './pages/admin/UserManagement'
import ListingModeration from './pages/admin/ListingModeration'
import Analytics from './pages/admin/Analytics'
import Settings from './pages/admin/Settings'
import AdminManagement from './pages/admin/AdminManagement'

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/user-home" element={<UserHomePage />} />
          <Route path="/resale" element={<Resale />} />
          <Route path="/predictions/laptop" element={<LaptopPrediction />} />
          <Route path="/predictions/smartphone" element={<SmartphonePrediction />} />
          <Route path="/sell-device" element={<CreateListing />} />
          <Route path="/smart-finder" element={<SmartProductFinder />} />
          <Route path="/marketplace" element={<Marketplace />} />
          <Route path="/marketplace/:id" element={<ProductDetails />} />
          <Route path="/messages" element={<Messages />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />

          {/* Protected Admin Routes */}
          <Route path="/admin" element={
            <ProtectedAdminRoute>
              <AdminLayout />
            </ProtectedAdminRoute>
          }>
            <Route index element={<AdminDashboard />} />
            <Route path="users" element={<UserManagement />} />
            <Route path="listings" element={<ListingModeration />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="settings" element={<Settings />} />
            <Route path="admins" element={<AdminManagement />} />
          </Route>
        </Routes>
      </Router>
    </ErrorBoundary>
  )
}

export default App
