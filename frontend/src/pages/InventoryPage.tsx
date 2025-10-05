import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import apiClient from '../api/client';
import type { InventoryItem } from '../api/types';
import InventoryGrid from '../components/Inventory/InventoryGrid';
import InventoryFilters from '../components/Inventory/InventoryFilters';
import './InventoryPage.css';

const InventoryPage = () => {
  const [filters, setFilters] = useState({
    condition: '',
    has_card: '',
  });

  const { data: inventory, isLoading, error } = useQuery<InventoryItem[]>({
    queryKey: ['inventory', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.condition) params.append('condition', filters.condition);
      if (filters.has_card) params.append('has_card', filters.has_card);
      
      const response = await apiClient.get(`/inventory/items/?${params.toString()}`);
      return response.data.results || response.data;
    },
  });

  return (
    <div className="inventory-page">
      <div className="inventory-header">
        <h1>Inventory Management</h1>
        <p>Manage your card collection status and condition</p>
      </div>

      <div className="inventory-controls">
        <InventoryFilters filters={filters} onFiltersChange={setFilters} />
      </div>

      {isLoading && <div className="loading">Loading inventory...</div>}
      {error && <div className="error">Error loading inventory</div>}
      {inventory && <InventoryGrid />}
    </div>
  );
};

export default InventoryPage;
