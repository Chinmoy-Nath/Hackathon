import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Layout from './components/common/Layout';
import LoginPage from './components/common/LoginPage';
import ProtectedRoute from './components/common/ProtectedRoute';
import DashboardPage from './pages/DashboardPage';
import CampaignList from './components/campaign/CampaignList';
import CreateCampaign from './components/campaign/CreateCampaign';
import CampaignDetail from './components/campaign/CampaignDetail';
import CustomersPage from './pages/CustomersPage';
import VehiclesPage from './pages/VehiclesPage';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="campaigns" element={<CampaignList />} />
            <Route path="campaigns/create" element={
              <ProtectedRoute allowedRoles={['campaign_manager']}>
                <CreateCampaign />
              </ProtectedRoute>
            } />
            <Route path="campaigns/:campaignId" element={<CampaignDetail />} />
            <Route path="customers" element={<CustomersPage />} />
            <Route path="vehicles" element={<VehiclesPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
