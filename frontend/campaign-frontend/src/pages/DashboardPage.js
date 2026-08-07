import React from 'react';
import { useAuth } from '../context/AuthContext';
import CampaignManagerDashboard from '../components/dashboards/CampaignManagerDashboard';
import RetailManagerDashboard from '../components/dashboards/RetailManagerDashboard';

function DashboardPage() {
  const { user } = useAuth();

  if (user?.role === 'retail_manager') {
    return <RetailManagerDashboard />;
  }
  return <CampaignManagerDashboard />;
}

export default DashboardPage;
