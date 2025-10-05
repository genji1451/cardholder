import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../../api/client';
import { getCardImageFromData } from '../../utils/imageUtils';
import './InventoryGrid.css';

const InventoryGrid = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCondition, setSelectedCondition] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  
  const queryClient = useQueryClient();

  // Fetch inventory data
  const { data: inventoryData, isLoading, error } = useQuery({
    queryKey: ['inventory'],
    queryFn: async () => {
      const response = await apiClient.get('/inventory/items/');
      return response.data.results || response.data;
    },
  });

  // Mutation for updating inventory items
  const updateInventoryMutation = useMutation({
    mutationFn: async ({ id, data }: { id: number; data: any }) => {
      return await apiClient.patch(`/inventory/items/${id}/`, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    },
  });

  // Mutation for deleting inventory items
  const deleteInventoryMutation = useMutation({
    mutationFn: async (id: number) => {
      return await apiClient.delete(`/inventory/items/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    },
  });

  const handleUpdateItem = (id: number, field: string, value: any) => {
    updateInventoryMutation.mutate({ id, data: { [field]: value } });
  };

  const handleDeleteItem = (id: number) => {
    if (window.confirm('Are you sure you want to remove this item from your collection?')) {
      deleteInventoryMutation.mutate(id);
    }
  };

  if (isLoading) {
    return (
      <div className="inventory-grid">
        <div className="loading">
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>🕸️</div>
          <p>Загружаем инвентарь...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="inventory-grid">
        <div className="error">
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>⚠️</div>
          <p>Ошибка загрузки инвентаря: {error.message}</p>
        </div>
      </div>
    );
  }

  // Filter inventory items
  const filteredItems = inventoryData?.filter((item: any) => {
    const matchesSearch = item.card?.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.card?.number.toString().includes(searchTerm);
    const matchesCondition = selectedCondition === 'all' || item.condition === selectedCondition;
    const matchesStatus = selectedStatus === 'all' || 
                         (selectedStatus === 'owned' && item.has_card) ||
                         (selectedStatus === 'missing' && !item.has_card);
    
    return matchesSearch && matchesCondition && matchesStatus;
  }) || [];

  // Calculate stats
  const totalItems = inventoryData?.length || 0;
  const ownedItems = inventoryData?.filter((item: any) => item.has_card).length || 0;
  const totalValue = inventoryData?.reduce((sum: number, item: any) => {
    if (item.has_card) {
      return sum + (item.quantity * parseFloat(item.card?.base_price_rub || 0));
    }
    return sum;
  }, 0) || 0;

  const getConditionColor = (condition: string) => {
    switch (condition) {
      case 'M': return '#16a34a'; // Mint
      case 'NM': return '#22c55e'; // Near Mint
      case 'SP': return '#eab308'; // Slightly Played
      case 'MP': return '#f97316'; // Moderately Played
      case 'HP': return '#dc2626'; // Heavily Played
      case 'DM': return '#991b1b'; // Damaged
      default: return '#6b7280';
    }
  };

  return (
    <div className="inventory-grid">
      {/* Header */}
      <div className="inventory-header">
        <div className="header-left">
          <div className="logo-section">
            <div className="spider-logo">🕷️</div>
            <h1 className="inventory-title">Инвентарь карточек Человек-Паук</h1>
          </div>
        </div>
        <div className="header-stats">
          <div className="stat-item">
            <span className="stat-number">{totalItems}</span>
            <span className="stat-label">Всего предметов</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{ownedItems}</span>
            <span className="stat-label">В коллекции</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">₽{totalValue.toFixed(2)}</span>
            <span className="stat-label">Общая стоимость</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="search-container">
          <input
            type="text"
            placeholder="Поиск карточек..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <div className="search-icon">🔍</div>
        </div>

        <div className="filter-buttons">
          <select
            value={selectedCondition}
            onChange={(e) => setSelectedCondition(e.target.value)}
            className="filter-select"
          >
            <option value="all">Все состояния</option>
            <option value="M">Отличное</option>
            <option value="NM">Почти отличное</option>
            <option value="SP">Слегка играно</option>
            <option value="MP">Умеренно играно</option>
            <option value="HP">Сильно играно</option>
            <option value="DM">Повреждено</option>
          </select>

          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="filter-select"
          >
            <option value="all">Все статусы</option>
            <option value="owned">В коллекции</option>
            <option value="missing">Отсутствует</option>
          </select>
        </div>
      </div>

      {/* Results count */}
      <div className="results-info">
        <p>Показано {filteredItems.length} из {totalItems} предметов</p>
      </div>

      {/* Inventory Grid */}
      <div className="items-grid">
        {filteredItems.map((item: any) => (
          <div key={item.id} className={`inventory-item ${item.has_card ? 'owned' : 'missing'}`}>
            <div className="item-header">
              <div className="item-number">#{item.card?.number}</div>
              <div className="item-actions">
                <button
                  className="action-btn delete"
                  onClick={() => handleDeleteItem(item.id)}
                  title="Remove from collection"
                >
                  🗑️
                </button>
              </div>
            </div>

            <div className="item-image">
              <img 
                src={getCardImageFromData(item.card)} 
                alt={item.card?.title}
                className="item-image-img"
                onError={(e) => {
                  // Если изображение не загрузилось, показываем заглушку
                  e.currentTarget.style.display = 'none';
                  const nextElement = e.currentTarget.nextElementSibling as HTMLElement;
                  if (nextElement) {
                    nextElement.style.display = 'flex';
                  }
                }}
              />
              <div className="item-placeholder" style={{ display: 'none' }}>
                🕷️
              </div>
              {item.has_card && <div className="owned-badge">✅</div>}
            </div>

            <div className="item-info">
              <h3 className="item-title">{item.card?.title}</h3>
              <p className="item-series">{item.card?.series_title}</p>
              <p className="item-price">₽{parseFloat(item.card?.base_price_rub || 0).toFixed(2)}</p>
            </div>

            <div className="item-details">
              <div className="detail-row">
                <label>Количество:</label>
                <input
                  type="number"
                  min="0"
                  value={item.quantity}
                  onChange={(e) => handleUpdateItem(item.id, 'quantity', parseInt(e.target.value))}
                  className="detail-input"
                />
              </div>

              <div className="detail-row">
                <label>Состояние:</label>
                <select
                  value={item.condition}
                  onChange={(e) => handleUpdateItem(item.id, 'condition', e.target.value)}
                  className="detail-select"
                  style={{ borderColor: getConditionColor(item.condition) }}
                >
                  <option value="NO">Не владею</option>
                  <option value="M">Отличное</option>
                  <option value="NM">Почти отличное</option>
                  <option value="SP">Слегка играно</option>
                  <option value="MP">Умеренно играно</option>
                  <option value="HP">Сильно играно</option>
                  <option value="DM">Повреждено</option>
                </select>
              </div>

              <div className="detail-row">
                <label>Статус:</label>
                <label className="switch">
                  <input
                    type="checkbox"
                    checked={item.has_card}
                    onChange={(e) => handleUpdateItem(item.id, 'has_card', e.target.checked)}
                  />
                  <span className="slider"></span>
                </label>
              </div>

              <div className="detail-row">
                <label>Рейтинг:</label>
                <input
                  type="number"
                  min="0"
                  max="5"
                  step="0.1"
                  value={item.user_rating || ''}
                  onChange={(e) => handleUpdateItem(item.id, 'user_rating', parseFloat(e.target.value))}
                  className="detail-input"
                  placeholder="0-5"
                />
              </div>
            </div>

            <div className="item-summary">
              <div className="summary-row">
                <span>Общая стоимость:</span>
                <span>₽{(item.quantity * parseFloat(item.card?.base_price_rub || 0)).toFixed(2)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredItems.length === 0 && (
        <div className="no-results">
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📦</div>
          <h3>Предметы не найдены</h3>
          <p>Попробуйте изменить поисковые запросы или фильтры</p>
        </div>
      )}
    </div>
  );
};

export default InventoryGrid;