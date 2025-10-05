import { useState } from 'react';
import './WishlistFilters.css';

interface WishlistFiltersProps {
  filters: {
    priority: string;
    card__rarity: string;
    card__series: string;
  };
  onFiltersChange: (filters: any) => void;
}

const WishlistFilters = ({ filters, onFiltersChange }: WishlistFiltersProps) => {
  const [isOpen, setIsOpen] = useState(false);

  const priorityOptions = [
    { value: '', label: 'All Priorities' },
    { value: '1', label: 'Low' },
    { value: '2', label: 'Medium' },
    { value: '3', label: 'High' },
  ];

  const rarityOptions = [
    { value: '', label: 'All Rarities' },
    { value: 'o', label: 'Обычная' },
    { value: 'ск', label: 'Средняя карта' },
    { value: 'ук', label: 'Ультра карта' },
  ];

  const seriesOptions = [
    { value: '', label: 'All Series' },
    { value: '1', label: 'Series 1' },
    { value: '2', label: 'Series 2' },
  ];

  const handleFilterChange = (key: string, value: string) => {
    onFiltersChange({
      ...filters,
      [key]: value,
    });
  };

  return (
    <div className="wishlist-filters">
      <button
        className="filters-toggle"
        onClick={() => setIsOpen(!isOpen)}
      >
        Filters {isOpen ? '▲' : '▼'}
      </button>
      
      {isOpen && (
        <div className="filters-content">
          <div className="filter-group">
            <label>Priority</label>
            <select
              value={filters.priority}
              onChange={(e) => handleFilterChange('priority', e.target.value)}
            >
              {priorityOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Rarity</label>
            <select
              value={filters.card__rarity}
              onChange={(e) => handleFilterChange('card__rarity', e.target.value)}
            >
              {rarityOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Series</label>
            <select
              value={filters.card__series}
              onChange={(e) => handleFilterChange('card__series', e.target.value)}
            >
              {seriesOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}
    </div>
  );
};

export default WishlistFilters;
