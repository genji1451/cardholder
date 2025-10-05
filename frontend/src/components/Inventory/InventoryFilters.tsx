import { useState } from 'react';
import './InventoryFilters.css';

interface InventoryFiltersProps {
  filters: {
    condition: string;
    has_card: string;
  };
  onFiltersChange: (filters: any) => void;
}

const InventoryFilters = ({ filters, onFiltersChange }: InventoryFiltersProps) => {
  const [isOpen, setIsOpen] = useState(false);

  const conditionOptions = [
    { value: '', label: 'All Conditions' },
    { value: 'M', label: 'Mint' },
    { value: 'NM', label: 'Near Mint' },
    { value: 'SP', label: 'Slightly Played' },
    { value: 'MP', label: 'Moderately Played' },
    { value: 'HP', label: 'Heavily Played' },
    { value: 'DM', label: 'Damaged' },
    { value: 'NO', label: 'Not Owned' },
  ];

  const ownershipOptions = [
    { value: '', label: 'All' },
    { value: 'true', label: 'Owned' },
    { value: 'false', label: 'Not Owned' },
  ];

  const handleFilterChange = (key: string, value: string) => {
    onFiltersChange({
      ...filters,
      [key]: value,
    });
  };

  return (
    <div className="inventory-filters">
      <button
        className="filters-toggle"
        onClick={() => setIsOpen(!isOpen)}
      >
        Filters {isOpen ? '▲' : '▼'}
      </button>
      
      {isOpen && (
        <div className="filters-content">
          <div className="filter-group">
            <label>Ownership</label>
            <select
              value={filters.has_card}
              onChange={(e) => handleFilterChange('has_card', e.target.value)}
            >
              {ownershipOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Condition</label>
            <select
              value={filters.condition}
              onChange={(e) => handleFilterChange('condition', e.target.value)}
            >
              {conditionOptions.map(option => (
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

export default InventoryFilters;
