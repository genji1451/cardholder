import { useQuery } from '@tanstack/react-query';
import apiClient from '../api/client';
import type { AnalyticsOverview } from '../api/types';
import OverviewCards from '../components/Dashboard/OverviewCards';
import TopExpensive from '../components/Dashboard/TopExpensive';
import Charts from '../components/Dashboard/Charts';
import SubscriptionChecker from '../components/SubscriptionChecker';
import './DashboardPage.css';

const DashboardPage = () => {
  const { data: overview, isLoading, error } = useQuery<AnalyticsOverview>({
    queryKey: ['analytics', 'overview'],
    queryFn: async () => {
      const response = await apiClient.get('/analytics/overview/');
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-container">
        <div className="loading">Loading dashboard...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-container">
        <div className="error">Error loading dashboard data</div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-container">
      <div className="dashboard-header">
          <h1>🕷️ Dashboard</h1>
        <p>Welcome to your Spider-Man cards collection</p>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-main">
          <OverviewCards overview={overview} />
          <Charts />
        </div>
        
        <div className="dashboard-sidebar">
          <SubscriptionChecker />
          <TopExpensive />
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
