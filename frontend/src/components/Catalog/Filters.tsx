import { useState } from 'react';
import './Filters.css';

interface FiltersProps {
  filters: {
    rarity: string;
    series: string;
  };
  onFiltersChange: (filters: any) => void;
}

const Filters = ({ filters, onFiltersChange }: FiltersProps) => {
  const [isOpen, setIsOpen] = useState(false);

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
    <div className="filters">
      <button
        className="filters-toggle"
        onClick={() => setIsOpen(!isOpen)}
      >
        Filters {isOpen ? '▲' : '▼'}
      </button>
      
      {isOpen && (
        <div className="filters-content">
          <div className="filter-group">
            <label>Rarity</label>
            <select
              value={filters.rarity}
              onChange={(e) => handleFilterChange('rarity', e.target.value)}
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
              value={filters.series}
              onChange={(e) => handleFilterChange('series', e.target.value)}
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

export default Filters;
