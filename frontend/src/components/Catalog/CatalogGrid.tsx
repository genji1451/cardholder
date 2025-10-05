import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../../api/client';
import { getCardImageFromData } from '../../utils/imageUtils';
import './CatalogGrid.css';

const CatalogGrid = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRarity, setSelectedRarity] = useState('all');
  const [selectedSeries, setSelectedSeries] = useState('all');
  const queryClient = useQueryClient();

  // Fetch cards data
  const { data: cardsData, isLoading, error } = useQuery({
    queryKey: ['cards'],
    queryFn: async () => {
      const response = await apiClient.get('/cards/');
      // Обрабатываем пагинацию - берем results если есть, иначе весь response
      return response.data.results || response.data;
    },
  });

  // Fetch inventory data to show which cards are owned
  const { data: inventoryData } = useQuery({
    queryKey: ['inventory'],
    queryFn: async () => {
      const response = await apiClient.get('/inventory/items/');
      return response.data.results || response.data;
    },
  });

  // Mutation for adding card to collection
  const addToCollectionMutation = useMutation({
    mutationFn: async (cardId: number) => {
      const response = await apiClient.post('/inventory/items/', {
        card_id: cardId,
        quantity: 1,
        condition: 'NM',
        user_rating: 8.0,
        has_card: true
      });
      return response.data;
    },
    onSuccess: () => {
      // Обновляем кэш инвентаря
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
    },
    onError: (error: any) => {
      console.error('Ошибка добавления в коллекцию:', error);
      // Если карточка уже есть в коллекции, обновляем кэш
      if (error.response?.status === 500 && error.response?.data?.includes('UNIQUE constraint')) {
        queryClient.invalidateQueries({ queryKey: ['inventory'] });
      }
    }
  });

  if (isLoading) {
    return (
      <div className="catalog-grid">
        <div className="loading">
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>🕸️</div>
          <p>Загружаем каталог...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="catalog-grid">
        <div className="error">
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>⚠️</div>
          <p>Ошибка загрузки каталога: {error.message}</p>
        </div>
      </div>
    );
  }

  // Filter cards based on search and filters
  const filteredCards = cardsData?.filter((card: any) => {
    const matchesSearch = card.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         card.number.toString().includes(searchTerm);
    const matchesRarity = selectedRarity === 'all' || card.rarity === selectedRarity;
    
    // Фильтрация по сериям на основе номера карточки
    let matchesSeries = true;
    if (selectedSeries !== 'all') {
      const cardNumber = card.number;
      if (selectedSeries === '1') {
        matchesSeries = cardNumber >= 1 && cardNumber <= 275;
      } else if (selectedSeries === '2') {
        matchesSeries = cardNumber >= 276 && cardNumber <= 550;
      } else if (selectedSeries === '3') {
        matchesSeries = cardNumber >= 551 && cardNumber <= 825;
      }
    }
    
    return matchesSearch && matchesRarity && matchesSeries;
  }) || [];

  // Get series options for filter
  const seriesOptions = [
    { value: '1', label: 'Часть 1 (1-275)' },
    { value: '2', label: 'Часть 2 (276-550)' },
    { value: '3', label: 'Часть 3 (551-825)' }
  ];

  // Get rarity display info
  const getRarityInfo = (rarity: string) => {
    switch (rarity) {
      case 'o': return { name: 'Common', emoji: '🟢', color: '#16a34a' };
      case 'ск': return { name: 'Uncommon', emoji: '🟡', color: '#eab308' };
      case 'ук': return { name: 'Rare', emoji: '🔴', color: '#dc2626' };
      default: return { name: 'Unknown', emoji: '⚪', color: '#6b7280' };
    }
  };

  // Check if card is owned
  const isCardOwned = (cardId: number) => {
    return inventoryData?.some((item: any) => item.card.id === cardId && item.has_card) || false;
  };

  // Handle add to collection
  const handleAddToCollection = (cardId: number) => {
    addToCollectionMutation.mutate(cardId);
  };

  return (
    <div className="catalog-grid">
      {/* Header */}
      <div className="catalog-header">
        <div className="header-left">
          <div className="logo-section">
            <div className="spider-logo">🕷️</div>
            <h1 className="catalog-title">Каталог карточек Человек-Паук</h1>
          </div>
        </div>
        <div className="header-stats">
          <div className="stat-item">
            <span className="stat-number">{cardsData?.length || 0}</span>
            <span className="stat-label">Всего карточек</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{inventoryData?.filter((item: any) => item.has_card).length || 0}</span>
            <span className="stat-label">В коллекции</span>
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
            value={selectedRarity}
            onChange={(e) => setSelectedRarity(e.target.value)}
            className="filter-select"
          >
            <option value="all">Все редкости</option>
            <option value="o">🟢 Обычная</option>
            <option value="ск">🟡 Необычная</option>
            <option value="ук">🔴 Редкая</option>
          </select>

          <select
            value={selectedSeries}
            onChange={(e) => setSelectedSeries(e.target.value)}
            className="filter-select"
          >
            <option value="all">Все серии</option>
            {seriesOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Results count */}
      <div className="results-info">
        <p>Показано {filteredCards.length} из {cardsData?.length || 0} карточек</p>
      </div>

      {/* Cards Grid */}
      <div className="cards-grid">
        {filteredCards.map((card: any) => {
          const rarityInfo = getRarityInfo(card.rarity);
          const owned = isCardOwned(card.id);

          return (
            <div key={card.id} className={`card-item ${owned ? 'owned' : 'missing'}`}>
              <div className="card-header">
                <div className="card-number">#{card.number}</div>
                <div className="card-rarity" style={{ color: rarityInfo.color }}>
                  {rarityInfo.emoji} {rarityInfo.name}
                </div>
              </div>

              <div className="card-image">
                <img 
                  src={getCardImageFromData(card)} 
                  alt={card.title}
                  className="card-image-img"
                  onError={(e) => {
                    // Если изображение не загрузилось, показываем заглушку
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
                {owned && <div className="owned-badge">✅</div>}
              </div>

              <div className="card-info">
                <h3 className="card-title">{card.title}</h3>
                <p className="card-series">
                  {card.number >= 1 && card.number <= 275 ? 'Часть 1' :
                   card.number >= 276 && card.number <= 550 ? 'Часть 2' :
                   card.number >= 551 && card.number <= 825 ? 'Часть 3' : 'Неизвестная часть'}
                </p>
                <div className="card-price">₽{parseFloat(card.base_price_rub).toFixed(2)}</div>
              </div>

              <div className="card-actions">
                <button 
                  className={`action-btn ${owned ? 'owned' : 'add'}`}
                  onClick={() => !owned && handleAddToCollection(card.id)}
                  disabled={owned || addToCollectionMutation.isPending}
                >
                  {addToCollectionMutation.isPending ? '⏳ Добавляем...' :
                   owned ? '✅ В коллекции' : '➕ Добавить в коллекцию'}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {filteredCards.length === 0 && (
        <div className="no-results">
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔍</div>
          <h3>Карточки не найдены</h3>
          <p>Попробуйте изменить поисковые запросы или фильтры</p>
        </div>
      )}
    </div>
  );
};

export default CatalogGrid;