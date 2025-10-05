import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';
import { getCardImageFromData } from '../utils/imageUtils';
import './SimplePortfolio.css';

const SimplePortfolio = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');
  const [selectedCards, setSelectedCards] = useState<number[]>([]);
  const [viewMode, setViewMode] = useState<'table' | 'grid'>('table');
  
  const queryClient = useQueryClient();

  // Fetch cards data
  const { data: cardsData, isLoading: cardsLoading, error: cardsError } = useQuery({
    queryKey: ['cards'],
    queryFn: async () => {
      const response = await apiClient.get('/cards/');
      return response.data.results || response.data;
    },
  });

  // Fetch inventory data
  const { data: inventoryData, isLoading: inventoryLoading, error: inventoryError } = useQuery({
    queryKey: ['inventory'],
    queryFn: async () => {
      const response = await apiClient.get('/inventory/items/');
      return response.data.results || response.data;
    },
  });

  // Fetch analytics data
  useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: async () => {
      const response = await apiClient.get('/analytics/overview/');
      return response.data;
    },
  });

  // Mutation for removing cards from inventory
  const removeFromInventoryMutation = useMutation({
    mutationFn: async (itemId: number) => {
      await apiClient.delete(`/inventory/items/${itemId}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
    },
    onError: (error) => {
      console.error('Ошибка удаления из коллекции:', error);
    }
  });

  // Mutation for updating inventory item
  const updateInventoryMutation = useMutation({
    mutationFn: async ({ itemId, data }: { itemId: number; data: any }) => {
      const response = await apiClient.patch(`/inventory/items/${itemId}/`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
    },
    onError: (error) => {
      console.error('Ошибка обновления карточки:', error);
    }
  });

  const isLoading = cardsLoading || inventoryLoading;

  // Debug information (commented out for production)
  // console.log('Portfolio Debug:', {
  //   cardsData,
  //   inventoryData,
  //   analyticsData,
  //   isLoading,
  //   cardsLoading,
  //   inventoryLoading,
  //   cardsError,
  //   inventoryError,
  //   analyticsError
  // });

  // Calculate portfolio stats
  const calculateStats = () => {
    if (!inventoryData || !cardsData) {
      return {
        invested: 0,
        currentValue: 0,
        profit: 0,
        netProfit: 0,
        ownedCount: 0,
        totalCount: cardsData?.length || 0
      };
    }

    const ownedCards = inventoryData.filter((item: any) => item.has_card);
    const totalInvested = ownedCards.reduce((sum: number, item: any) => {
      const price = parseFloat(item.card?.base_price_rub || 0);
      const quantity = item.quantity || 0;
      return sum + (price * quantity);
    }, 0);
    
    const currentValue = ownedCards.reduce((sum: number, item: any) => {
      const price = parseFloat(item.card?.base_price_rub || 0);
      const quantity = item.quantity || 0;
      return sum + (price * quantity);
    }, 0);

    const profit = currentValue - totalInvested;
    const netProfit = profit;

    return {
      invested: totalInvested,
      currentValue,
      profit,
      netProfit,
      ownedCount: ownedCards.length,
      totalCount: cardsData.length
    };
  };

  const stats = calculateStats();

  // Enhanced filtering and sorting logic
  const filteredAndSortedCards = useMemo(() => {
    if (!cardsData) return [];

    let filtered = cardsData.filter((card: any) => {
      const matchesSearch = card.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           card.number.toString().includes(searchTerm);
      
      if (selectedFilter === 'owned') {
        const inventoryItem = inventoryData?.find((item: any) => 
          item.card.id === card.id && item.has_card
        );
        return matchesSearch && inventoryItem;
      } else if (selectedFilter === 'missing') {
        const inventoryItem = inventoryData?.find((item: any) => 
          item.card.id === card.id && item.has_card
        );
        return matchesSearch && !inventoryItem;
      }
      
      return matchesSearch;
    });

    // Sort cards
    filtered.sort((a: any, b: any) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'name':
          aValue = a.title.toLowerCase();
          bValue = b.title.toLowerCase();
          break;
        case 'number':
          aValue = a.number;
          bValue = b.number;
          break;
        case 'price':
          aValue = parseFloat(a.base_price_rub || 0);
          bValue = parseFloat(b.base_price_rub || 0);
          break;
        case 'rarity':
          const rarityOrder = { 'o': 1, 'ск': 2, 'ук': 3 };
          aValue = rarityOrder[a.rarity as keyof typeof rarityOrder] || 0;
          bValue = rarityOrder[b.rarity as keyof typeof rarityOrder] || 0;
          break;
        default:
          aValue = a.title.toLowerCase();
          bValue = b.title.toLowerCase();
      }

      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

    return filtered;
  }, [cardsData, inventoryData, searchTerm, selectedFilter, sortBy, sortOrder]);

  // Helper functions
  const handleRemoveFromCollection = (itemId: number) => {
    if (window.confirm('Удалить карточку из коллекции?')) {
      removeFromInventoryMutation.mutate(itemId);
    }
  };

  const handleUpdateQuantity = (itemId: number, newQuantity: number) => {
    if (newQuantity <= 0) {
      handleRemoveFromCollection(itemId);
    } else {
      updateInventoryMutation.mutate({
        itemId,
        data: { quantity: newQuantity }
      });
    }
  };

  const handleUpdateCondition = (itemId: number, newCondition: string) => {
    updateInventoryMutation.mutate({
      itemId,
      data: { condition: newCondition }
    });
  };

  const handleUpdateRating = (itemId: number, newRating: number) => {
    updateInventoryMutation.mutate({
      itemId,
      data: { user_rating: newRating }
    });
  };

  const toggleCardSelection = (cardId: number) => {
    setSelectedCards(prev => 
      prev.includes(cardId) 
        ? prev.filter(id => id !== cardId)
        : [...prev, cardId]
    );
  };

  const selectAllCards = () => {
    setSelectedCards(filteredAndSortedCards.map((card: any) => card.id));
  };

  const clearSelection = () => {
    setSelectedCards([]);
  };

  if (isLoading) {
    return (
      <div className="simple-portfolio">
        <div className="loading">
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>🕸️</div>
          <p>Загружаем ваше портфолио...</p>
          <p style={{ fontSize: '0.9rem', opacity: 0.7 }}>
            Карточки: {cardsLoading ? 'Загрузка...' : 'Загружено'} | 
            Инвентарь: {inventoryLoading ? 'Загрузка...' : 'Загружено'}
          </p>
        </div>
      </div>
    );
  }

  // Show error if there are critical errors
  if (cardsError || inventoryError) {
    return (
      <div className="simple-portfolio">
        <div className="error">
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>⚠️</div>
          <h2>Ошибка загрузки портфолио</h2>
          <p>Ошибка карточек: {cardsError?.message || 'Нет'}</p>
          <p>Ошибка инвентаря: {inventoryError?.message || 'Нет'}</p>
          <p>Проверьте, запущен ли сервер на порту 8000</p>
        </div>
      </div>
    );
  }

  // Debug display (commented out for production)
  // const debugInfo = (
  //   <div style={{ 
  //     background: 'rgba(255, 0, 0, 0.1)', 
  //     border: '1px solid red', 
  //     padding: '1rem', 
  //     margin: '1rem 0',
  //     borderRadius: '8px',
  //     color: 'white'
  //   }}>
  //     <h3>Debug Info:</h3>
  //     <p>Cards: {cardsData?.length || 0}</p>
  //     <p>Inventory: {inventoryData?.length || 0}</p>
  //     <p>Analytics: {analyticsData ? 'Yes' : 'No'}</p>
  //     <p>Loading: {isLoading ? 'Yes' : 'No'}</p>
  //     <p>Cards Loading: {cardsLoading ? 'Yes' : 'No'}</p>
  //     <p>Inventory Loading: {inventoryLoading ? 'Yes' : 'No'}</p>
  //     <p>Cards Error: {cardsError ? 'Yes' : 'No'}</p>
  //     <p>Inventory Error: {inventoryError ? 'Yes' : 'No'}</p>
  //     <p>Analytics Error: {analyticsError ? 'Yes' : 'No'}</p>
  //   </div>
  // );

  return (
    <div className="simple-portfolio">
      {/* Header */}
      <div className="portfolio-header">
        <div className="header-left">
          <div className="logo-section">
            <div className="spider-logo">🕷️</div>
            <h1 className="portfolio-title">Портфолио карточек Человек-Паук</h1>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-section">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">Инвестировано</div>
            <div className="stat-value">₽{stats.invested.toFixed(2)}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Текущая стоимость</div>
            <div className="stat-value">₽{stats.currentValue.toFixed(2)}</div>
          </div>
          <div className="stat-card profit">
            <div className="stat-label">Прибыль</div>
            <div className="stat-value">₽{stats.profit.toFixed(2)}</div>
          </div>
          <div className="stat-card profit">
            <div className="stat-label">Чистая прибыль</div>
            <div className="stat-value">₽{stats.netProfit.toFixed(2)}</div>
          </div>
        </div>
      </div>

      {/* Enhanced Action Bar */}
      <div className="action-bar">
        <div className="search-section">
          <div className="search-input-container">
            <input
              type="text"
              placeholder="Поиск карточек..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            <div className="search-icon">🔍</div>
          </div>
        </div>
        
        <div className="filter-buttons">
          <button 
            className={`filter-btn ${selectedFilter === 'all' ? 'active' : ''}`}
            onClick={() => setSelectedFilter('all')}
          >
            📊 Все ({filteredAndSortedCards.length})
          </button>
          <button 
            className={`filter-btn ${selectedFilter === 'owned' ? 'active' : ''}`}
            onClick={() => setSelectedFilter('owned')}
          >
            💼 В коллекции ({stats.ownedCount})
          </button>
          <button 
            className={`filter-btn ${selectedFilter === 'missing' ? 'active' : ''}`}
            onClick={() => setSelectedFilter('missing')}
          >
            📥 Отсутствуют ({stats.totalCount - stats.ownedCount})
          </button>
        </div>

        <div className="sort-controls">
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
            className="sort-select"
          >
            <option value="name">По названию</option>
            <option value="number">По номеру</option>
            <option value="price">По цене</option>
            <option value="rarity">По редкости</option>
          </select>
          <button 
            className={`sort-btn ${sortOrder === 'asc' ? 'active' : ''}`}
            onClick={() => setSortOrder('asc')}
          >
            ↑
          </button>
          <button 
            className={`sort-btn ${sortOrder === 'desc' ? 'active' : ''}`}
            onClick={() => setSortOrder('desc')}
          >
            ↓
          </button>
        </div>

        <div className="view-controls">
          <button 
            className={`view-btn ${viewMode === 'table' ? 'active' : ''}`}
            onClick={() => setViewMode('table')}
          >
            📋 Таблица
          </button>
          <button 
            className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
            onClick={() => setViewMode('grid')}
          >
            🎴 Сетка
          </button>
        </div>

        <div className="action-buttons">
          {selectedCards.length > 0 && (
            <div className="selection-actions">
              <span className="selection-count">Выбрано: {selectedCards.length}</span>
              <button 
                className="action-btn danger"
                onClick={clearSelection}
              >
                ❌ Очистить
              </button>
            </div>
          )}
          
          <button 
            className="action-btn"
            onClick={selectAllCards}
          >
            ✅ Выбрать все
          </button>
          <button 
            className="action-btn"
            onClick={() => {/* TODO: Implement add cards modal */}}
          >
            ➕ Добавить карточки
          </button>
          <button className="action-btn">
            📤 Экспорт
          </button>
          <button className="action-btn">
            📈 Аналитика
          </button>
        </div>
      </div>

      {/* Enhanced Table/Grid Section */}
      <div className="table-section">
        {viewMode === 'table' ? (
          <div className="table-container">
            <table className="cards-table">
              <thead>
                <tr>
                  <th>
                    <input 
                      type="checkbox" 
                      checked={selectedCards.length === filteredAndSortedCards.length && filteredAndSortedCards.length > 0}
                      onChange={(e) => e.target.checked ? selectAllCards() : clearSelection()}
                    />
                  </th>
                  <th>Изображение</th>
                  <th>Название</th>
                  <th>Количество</th>
                  <th>Состояние</th>
                  <th>Рейтинг</th>
                  <th>Цена</th>
                  <th>Стоимость</th>
                  <th>Статус</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {filteredAndSortedCards.length === 0 ? (
                  <tr>
                    <td colSpan={10} className="empty-state">
                      <div className="empty-content">
                        <div className="spider-logo">🕷️</div>
                        <p>Карточки не найдены</p>
                      </div>
                    </td>
                  </tr>
                ) : (
                  filteredAndSortedCards.map((card: any) => {
                    const inventoryItem = inventoryData?.find((item: any) => 
                      item.card.id === card.id
                    );
                    
                    const isOwned = inventoryItem?.has_card || false;
                    const quantity = inventoryItem?.quantity || 0;
                    const condition = inventoryItem?.condition || 'NM';
                    const rating = Math.max(0, Math.min(10, parseFloat(inventoryItem?.user_rating || 0)));
                    const price = parseFloat(card.base_price_rub || 0);
                    const totalValue = quantity * price;

                    return (
                      <tr key={card.id} className={`${isOwned ? 'owned' : 'missing'} ${selectedCards.includes(card.id) ? 'selected' : ''}`}>
                        <td>
                          <input 
                            type="checkbox" 
                            checked={selectedCards.includes(card.id)}
                            onChange={() => toggleCardSelection(card.id)}
                          />
                        </td>
                        <td>
                          <div className="card-image-small">
                            <img 
                              src={getCardImageFromData(card)} 
                              alt={card.title}
                                     onError={(e) => {
                                       e.currentTarget.style.display = 'none';
                                       const nextElement = e.currentTarget.nextElementSibling as HTMLElement;
                                       if (nextElement) {
                                         nextElement.style.display = 'flex';
                                       }
                                     }}
                            />
                            <div className="card-placeholder" style={{ display: 'none' }}>
                              🕷️
                            </div>
                          </div>
                        </td>
                        <td>
                          <div className="card-name">
                            <strong>{card.title}</strong>
                            <span className="card-number">#{card.number}</span>
                            <div className="rarity-badge">
                              {card.rarity === 'o' ? '🟢 Обычная' : 
                               card.rarity === 'ск' ? '🟡 Необычная' : '🔴 Редкая'}
                            </div>
                          </div>
                        </td>
                        <td>
                          {isOwned && inventoryItem ? (
                            <div className="quantity-controls">
                              <button 
                                onClick={() => handleUpdateQuantity(inventoryItem.id, quantity - 1)}
                                className="qty-btn"
                              >
                                -
                              </button>
                              <span className="quantity">{quantity}</span>
                              <button 
                                onClick={() => handleUpdateQuantity(inventoryItem.id, quantity + 1)}
                                className="qty-btn"
                              >
                                +
                              </button>
                            </div>
                          ) : (
                            <span className="no-quantity">-</span>
                          )}
                        </td>
                        <td>
                          {isOwned && inventoryItem ? (
                            <select 
                              value={condition}
                              onChange={(e) => handleUpdateCondition(inventoryItem.id, e.target.value)}
                              className="condition-select"
                            >
                              <option value="M">M - Отличное</option>
                              <option value="NM">NM - Почти отличное</option>
                              <option value="SP">SP - Хорошее</option>
                              <option value="MP">MP - Удовлетворительное</option>
                            </select>
                          ) : (
                            <span className="no-condition">-</span>
                          )}
                        </td>
                        <td>
                          {isOwned && inventoryItem ? (
                            <div className="rating-controls">
                              <input 
                                type="number" 
                                min="1" 
                                max="10" 
                                step="0.1"
                                value={rating}
                                onChange={(e) => handleUpdateRating(inventoryItem.id, parseFloat(e.target.value))}
                                className="rating-input"
                              />
                              <span className="rating-stars">
                                {(() => {
                                  const filledStars = Math.max(0, Math.min(5, Math.floor(rating)));
                                  const emptyStars = Math.max(0, 5 - filledStars);
                                  return '★'.repeat(filledStars) + '☆'.repeat(emptyStars);
                                })()}
                              </span>
                            </div>
                          ) : (
                            <span className="no-rating">-</span>
                          )}
                        </td>
                        <td>₽{price.toFixed(2)}</td>
                        <td>₽{totalValue.toFixed(2)}</td>
                        <td>
                          <span className={`status-badge ${isOwned ? 'owned' : 'missing'}`}>
                            {isOwned ? '✅ В коллекции' : '❌ Отсутствует'}
                          </span>
                        </td>
                        <td>
                          <div className="action-buttons-cell">
                            {isOwned && inventoryItem && (
                              <button 
                                className="action-btn-small danger"
                                onClick={() => handleRemoveFromCollection(inventoryItem.id)}
                                title="Удалить из коллекции"
                              >
                                🗑️
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="cards-grid">
            {filteredAndSortedCards.map((card: any) => {
              const inventoryItem = inventoryData?.find((item: any) => 
                item.card.id === card.id
              );
              
              const isOwned = inventoryItem?.has_card || false;
              const quantity = inventoryItem?.quantity || 0;
              const price = parseFloat(card.base_price_rub || 0);
              const totalValue = quantity * price;

              return (
                <div key={card.id} className={`card-item ${isOwned ? 'owned' : 'missing'} ${selectedCards.includes(card.id) ? 'selected' : ''}`}>
                  <div className="card-checkbox">
                    <input 
                      type="checkbox" 
                      checked={selectedCards.includes(card.id)}
                      onChange={() => toggleCardSelection(card.id)}
                    />
                  </div>
                  <div className="card-image">
                    <img 
                      src={getCardImageFromData(card)} 
                      alt={card.title}
                                     onError={(e) => {
                                       e.currentTarget.style.display = 'none';
                                       const nextElement = e.currentTarget.nextElementSibling as HTMLElement;
                                       if (nextElement) {
                                         nextElement.style.display = 'flex';
                                       }
                                     }}
                    />
                    <div className="card-placeholder" style={{ display: 'none' }}>
                      🕷️
                    </div>
                    {isOwned && <div className="owned-badge">✅</div>}
                  </div>
                  <div className="card-info">
                    <h3 className="card-title">{card.title}</h3>
                    <p className="card-number">#{card.number}</p>
                    <div className="card-rarity">
                      {card.rarity === 'o' ? '🟢 Обычная' : 
                       card.rarity === 'ск' ? '🟡 Необычная' : '🔴 Редкая'}
                    </div>
                    <div className="card-price">₽{price.toFixed(2)}</div>
                    {isOwned && (
                      <div className="card-stats">
                        <p>Количество: {quantity}</p>
                        <p>Стоимость: ₽{totalValue.toFixed(2)}</p>
                      </div>
                    )}
                  </div>
                  <div className="card-actions">
                    {isOwned && inventoryItem && (
                      <button 
                        className="action-btn-small danger"
                        onClick={() => handleRemoveFromCollection(inventoryItem.id)}
                      >
                        🗑️ Удалить
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default SimplePortfolio;
