import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import apiClient from '../api/client';
import type { Card } from '../api/types';
import CatalogGrid from '../components/Catalog/CatalogGrid';
import Filters from '../components/Catalog/Filters';
import Search from '../components/Catalog/Search';
import './CatalogPage.css';

const CatalogPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    rarity: '',
    series: '',
  });

  const { data: cards, isLoading, error } = useQuery<Card[]>({
    queryKey: ['cards', searchTerm, filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (filters.rarity) params.append('rarity', filters.rarity);
      if (filters.series) params.append('series', filters.series);
      
      const response = await apiClient.get(`/cards/?${params.toString()}`);
      return response.data.results || response.data;
    },
  });

  return (
    <div className="catalog-page">
      <div className="catalog-header">
        <h1>Card Catalog</h1>
        <p>Browse and search your Spider-Man card collection</p>
      </div>

      <div className="catalog-controls">
        <Search value={searchTerm} onChange={setSearchTerm} />
        <Filters filters={filters} onFiltersChange={setFilters} />
      </div>

      {isLoading && <div className="loading">Loading cards...</div>}
      {error && <div className="error">Error loading cards</div>}
      {cards && <CatalogGrid />}
    </div>
  );
};

export default CatalogPage;
