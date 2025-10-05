import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';
import type { WishlistItem, Card } from '../api/types';
import { getCardImageFromData } from '../utils/imageUtils';
import './WishlistPage.css';

const WishlistPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedCard, setSelectedCard] = useState<Card | null>(null);
  const [priority, setPriority] = useState<1 | 2 | 3>(2);
  const [targetPrice, setTargetPrice] = useState('');
  const [note, setNote] = useState('');
  
  const queryClient = useQueryClient();

  // Fetch wishlist data
  const { data: wishlistData, isLoading: wishlistLoading, error: wishlistError } = useQuery({
    queryKey: ['wishlist'],
    queryFn: async () => {
      const response = await apiClient.get('/wishlist/items/');
      return response.data.results || response.data;
    },
  });

  // Fetch cards data for adding to wishlist
  const { data: cardsData, isLoading: cardsLoading } = useQuery({
    queryKey: ['cards'],
    queryFn: async () => {
      const response = await apiClient.get('/cards/');
      return response.data.results || response.data;
    },
  });

  // Fetch inventory data to check what's already owned
  const { data: inventoryData } = useQuery({
    queryKey: ['inventory'],
    queryFn: async () => {
      const response = await apiClient.get('/inventory/items/');
      return response.data.results || response.data;
    },
  });

  // Mutation for adding to wishlist
  const addToWishlistMutation = useMutation({
    mutationFn: async (data: { card_id: number; priority: number; target_price_rub?: number; note: string }) => {
      const response = await apiClient.post('/wishlist/items/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['wishlist'] });
      setShowAddModal(false);
      setSelectedCard(null);
      setPriority(2);
      setTargetPrice('');
      setNote('');
    },
    onError: (error) => {
      console.error('Ошибка добавления в список желаний:', error);
    }
  });

  // Mutation for removing from wishlist
  const removeFromWishlistMutation = useMutation({
    mutationFn: async (itemId: number) => {
      await apiClient.delete(`/wishlist/items/${itemId}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['wishlist'] });
    },
    onError: (error) => {
      console.error('Ошибка удаления из списка желаний:', error);
    }
  });

  // Filter and search cards
  const filteredCards = useMemo(() => {
    if (!cardsData) return [];

    return cardsData.filter((card: Card) => {
      const matchesSearch = card.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           card.number.toString().includes(searchTerm);
      
      if (selectedFilter === 'missing') {
        const isOwned = inventoryData?.some((item: any) => 
          item.card?.id === card.id && item.has_card
        );
        return matchesSearch && !isOwned;
      } else if (selectedFilter === 'owned') {
        const isOwned = inventoryData?.some((item: any) => 
          item.card?.id === card.id && item.has_card
        );
        return matchesSearch && isOwned;
      }
      
      return matchesSearch;
    });
  }, [cardsData, inventoryData, searchTerm, selectedFilter]);

  const handleAddToWishlist = (card: Card) => {
    setSelectedCard(card);
    setShowAddModal(true);
  };

  const handleSubmitWishlist = () => {
    if (!selectedCard) return;

    addToWishlistMutation.mutate({
      card_id: selectedCard.id,
      priority,
      target_price_rub: targetPrice ? parseFloat(targetPrice) : undefined,
      note
    });
  };

  const handleRemoveFromWishlist = (itemId: number) => {
    if (window.confirm('Удалить карточку из списка желаний?')) {
      removeFromWishlistMutation.mutate(itemId);
    }
  };

  const isLoading = wishlistLoading || cardsLoading;

  if (isLoading) {
    return (
      <div className="wishlist-page">
        <div className="loading">
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>💝</div>
          <p>Загружаем список желаний...</p>
        </div>
      </div>
    );
  }

  if (wishlistError) {
    return (
      <div className="wishlist-page">
        <div className="error">
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>⚠️</div>
          <h2>Ошибка загрузки списка желаний</h2>
          <p>{wishlistError.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="wishlist-page">
      {/* Header */}
      <div className="wishlist-header">
        <div className="header-content">
          <div className="spider-logo">💝</div>
          <div>
            <h1>Список желаний</h1>
            <p>Отслеживайте карточки, которые хотите добавить в коллекцию</p>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="wishlist-stats">
        <div className="stat-card">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <div className="stat-label">В списке желаний</div>
            <div className="stat-value">{wishlistData?.length || 0}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🎯</div>
          <div className="stat-content">
            <div className="stat-label">Высокий приоритет</div>
            <div className="stat-value">
              {wishlistData?.filter((item: WishlistItem) => item.priority === 3).length || 0}
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">💰</div>
          <div className="stat-content">
            <div className="stat-label">С целевой ценой</div>
            <div className="stat-value">
              {wishlistData?.filter((item: WishlistItem) => item.target_price_rub).length || 0}
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="wishlist-controls">
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
            📊 Все
          </button>
          <button 
            className={`filter-btn ${selectedFilter === 'missing' ? 'active' : ''}`}
            onClick={() => setSelectedFilter('missing')}
          >
            ❌ Отсутствуют
          </button>
          <button 
            className={`filter-btn ${selectedFilter === 'owned' ? 'active' : ''}`}
            onClick={() => setSelectedFilter('owned')}
          >
            ✅ В коллекции
          </button>
        </div>

        <div className="action-buttons">
          <button 
            className="action-btn primary"
            onClick={() => setShowAddModal(true)}
          >
            ➕ Добавить в список желаний
          </button>
        </div>
      </div>

      {/* Wishlist Items */}
      <div className="wishlist-content">
        {wishlistData && wishlistData.length > 0 ? (
          <div className="wishlist-grid">
            {wishlistData.map((item: WishlistItem) => (
              <div key={item.id} className="wishlist-item">
                <div className="item-image">
                  <img 
                    src={getCardImageFromData(item.card)} 
                    alt={item.card.title}
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
                
                <div className="item-content">
                  <div className="item-header">
                    <div className="item-number">#{item.card.number}</div>
                    <div 
                      className="priority-badge"
                      style={{ 
                        backgroundColor: item.priority === 3 ? '#e31937' : 
                                        item.priority === 2 ? '#ff9800' : '#4caf50'
                      }}
                    >
                      {item.priority === 3 ? 'Высокий' : 
                       item.priority === 2 ? 'Средний' : 'Низкий'}
                    </div>
                  </div>
                  
                  <h3 className="item-title">{item.card.title}</h3>
                  <div className="item-series">
                    {item.card.number >= 1 && item.card.number <= 275 ? 'Часть 1' :
                     item.card.number >= 276 && item.card.number <= 550 ? 'Часть 2' : 'Часть 3'}
                  </div>
                  
                  <div className="item-details">
                    <div className="detail-row">
                      <span className="detail-label">Редкость:</span>
                      <span className={`detail-value rarity-badge ${item.card.rarity}`}>
                        {item.card.rarity === 'o' ? '🟢 Обычная' : 
                         item.card.rarity === 'ск' ? '🟡 Необычная' : '🔴 Редкая'}
                      </span>
                    </div>
                    
                    {item.target_price_rub && (
                      <div className="detail-row">
                        <span className="detail-label">Целевая цена:</span>
                        <span className="detail-value price">₽{item.target_price_rub}</span>
                      </div>
                    )}
                    
                    <div className="detail-row">
                      <span className="detail-label">Добавлено:</span>
                      <span className="detail-value date">
                        {new Date(item.created_at).toLocaleDateString('ru-RU')}
                      </span>
                    </div>
                  </div>
                  
                  {item.note && (
                    <p className="item-note">{item.note}</p>
                  )}
                </div>
                
                <div className="item-actions">
                  <button 
                    className="action-btn-small danger"
                    onClick={() => handleRemoveFromWishlist(item.id)}
                    title="Удалить из списка желаний"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-content">
              <div className="spider-logo">💝</div>
              <h3>Список желаний пуст</h3>
              <p>Добавьте карточки, которые хотите получить</p>
              <button 
                className="action-btn primary"
                onClick={() => setShowAddModal(true)}
              >
                ➕ Добавить карточки
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Add to Wishlist Modal */}
      {showAddModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Добавить в список желаний</h3>
              <button 
                className="modal-close"
                onClick={() => setShowAddModal(false)}
              >
                ✕
              </button>
            </div>
            
            <div className="modal-body">
              <div className="cards-grid">
                {filteredCards.slice(0, 20).map((card: Card) => (
                  <div 
                    key={card.id} 
                    className="card-item"
                    onClick={() => handleAddToWishlist(card)}
                  >
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
                    </div>
                    <div className="card-info">
                      <h4>{card.title}</h4>
                      <p>#{card.number}</p>
                      <div className="card-rarity">
                        {card.rarity === 'o' ? '🟢 Обычная' : 
                         card.rarity === 'ск' ? '🟡 Необычная' : '🔴 Редкая'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Wishlist Item Modal */}
      {selectedCard && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Добавить "{selectedCard.title}" в список желаний</h3>
              <button 
                className="modal-close"
                onClick={() => setSelectedCard(null)}
              >
                ✕
              </button>
            </div>
            
            <div className="modal-body">
              <div className="form-group">
                <label>Приоритет:</label>
                <select 
                  value={priority} 
                  onChange={(e) => setPriority(Number(e.target.value) as 1 | 2 | 3)}
                >
                  <option value={1}>Низкий</option>
                  <option value={2}>Средний</option>
                  <option value={3}>Высокий</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Целевая цена (₽):</label>
                <input 
                  type="number" 
                  value={targetPrice}
                  onChange={(e) => setTargetPrice(e.target.value)}
                  placeholder="Необязательно"
                />
              </div>
              
              <div className="form-group">
                <label>Заметка:</label>
                <textarea 
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  placeholder="Дополнительная информация..."
                  rows={3}
                />
              </div>
            </div>
            
            <div className="modal-footer">
              <button 
                className="action-btn secondary"
                onClick={() => setSelectedCard(null)}
              >
                Отмена
              </button>
              <button 
                className="action-btn primary"
                onClick={handleSubmitWishlist}
                disabled={addToWishlistMutation.isPending}
              >
                {addToWishlistMutation.isPending ? 'Добавление...' : 'Добавить'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WishlistPage;