import { useQuery } from '@tanstack/react-query';
import { useMemo } from 'react';
import apiClient from '../api/client';
// import type { AnalyticsOverview } from '../api/types';
import './AnalyticsPage.css';

const AnalyticsPage = () => {
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

  const isLoading = cardsLoading || inventoryLoading;

  // Calculate detailed analytics
  const analytics = useMemo(() => {
    if (!cardsData || !inventoryData) {
      return {
        totalCards: 0,
        ownedCards: 0,
        missingCards: 0,
        completionPercentage: 0,
        totalValue: 0,
        seriesStats: [],
        rarityStats: [],
        topCards: [],
        recentAdditions: []
      };
    }

    const ownedCards = inventoryData.filter((item: any) => item.has_card);
    const totalCards = cardsData.length;
    const missingCards = totalCards - ownedCards.length;
    const completionPercentage = totalCards > 0 ? (ownedCards.length / totalCards) * 100 : 0;

    // Calculate total value
    const totalValue = ownedCards.reduce((sum: number, item: any) => {
      const price = parseFloat(item.card?.base_price_rub || 0);
      const quantity = item.quantity || 0;
      return sum + (price * quantity);
    }, 0);

    // Series statistics
    const seriesStats = [
      {
        name: 'Часть 1 (1-275)',
        total: cardsData.filter((card: any) => card.number >= 1 && card.number <= 275).length,
        owned: ownedCards.filter((item: any) => item.card?.number >= 1 && item.card?.number <= 275).length,
        percentage: 0
      },
      {
        name: 'Часть 2 (276-550)',
        total: cardsData.filter((card: any) => card.number >= 276 && card.number <= 550).length,
        owned: ownedCards.filter((item: any) => item.card?.number >= 276 && item.card?.number <= 550).length,
        percentage: 0
      },
      {
        name: 'Часть 3 (551-825)',
        total: cardsData.filter((card: any) => card.number >= 551 && card.number <= 825).length,
        owned: ownedCards.filter((item: any) => item.card?.number >= 551 && item.card?.number <= 825).length,
        percentage: 0
      }
    ].map(series => ({
      ...series,
      percentage: series.total > 0 ? (series.owned / series.total) * 100 : 0
    }));

    // Rarity statistics
    const rarityStats = [
      {
        name: 'Обычные',
        rarity: 'o',
        total: cardsData.filter((card: any) => card.rarity === 'o').length,
        owned: ownedCards.filter((item: any) => item.card?.rarity === 'o').length,
        percentage: 0
      },
      {
        name: 'Необычные',
        rarity: 'ск',
        total: cardsData.filter((card: any) => card.rarity === 'ск').length,
        owned: ownedCards.filter((item: any) => item.card?.rarity === 'ск').length,
        percentage: 0
      },
      {
        name: 'Редкие',
        rarity: 'ук',
        total: cardsData.filter((card: any) => card.rarity === 'ук').length,
        owned: ownedCards.filter((item: any) => item.card?.rarity === 'ук').length,
        percentage: 0
      }
    ].map(rarity => ({
      ...rarity,
      percentage: rarity.total > 0 ? (rarity.owned / rarity.total) * 100 : 0
    }));

    // Top valuable cards
    const topCards = ownedCards
      .map((item: any) => ({
        ...item,
        value: parseFloat(item.card?.base_price_rub || 0) * (item.quantity || 0)
      }))
      .sort((a: any, b: any) => b.value - a.value)
      .slice(0, 10);

    // Recent additions (mock data for now)
    const recentAdditions = ownedCards.slice(-5);

    return {
      totalCards,
      ownedCards: ownedCards.length,
      missingCards,
      completionPercentage,
      totalValue,
      seriesStats,
      rarityStats,
      topCards,
      recentAdditions
    };
  }, [cardsData, inventoryData]);

  if (isLoading) {
    return (
      <div className="analytics-page">
        <div className="loading">
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>📊</div>
          <p>Загружаем аналитику...</p>
        </div>
      </div>
    );
  }

  if (cardsError || inventoryError) {
    return (
      <div className="analytics-page">
        <div className="error">
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>⚠️</div>
          <h2>Ошибка загрузки аналитики</h2>
          <p>Карточки: {cardsError?.message || 'Нет'}</p>
          <p>Инвентарь: {inventoryError?.message || 'Нет'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-page">
      <div className="analytics-header">
        <div className="header-content">
          <div className="spider-logo">🕷️</div>
          <div>
            <h1>Аналитика коллекции</h1>
            <p>Детальная статистика вашей коллекции карточек Человек-Паук</p>
          </div>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="stats-section">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <div className="stat-label">Всего карточек</div>
              <div className="stat-value">{analytics.totalCards}</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">✅</div>
            <div className="stat-content">
              <div className="stat-label">В коллекции</div>
              <div className="stat-value">{analytics.ownedCards}</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">❌</div>
            <div className="stat-content">
              <div className="stat-label">Отсутствуют</div>
              <div className="stat-value">{analytics.missingCards}</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">📈</div>
            <div className="stat-content">
              <div className="stat-label">Завершенность</div>
              <div className="stat-value">{analytics.completionPercentage.toFixed(1)}%</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">💰</div>
            <div className="stat-content">
              <div className="stat-label">Общая стоимость</div>
              <div className="stat-value">₽{analytics.totalValue.toFixed(2)}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-section">
        <div className="charts-grid">
          {/* Series Progress */}
          <div className="chart-container">
            <h3>Прогресс по сериям</h3>
            <div className="series-progress">
              {analytics.seriesStats.map((series, index) => (
                <div key={index} className="series-item">
                  <div className="series-header">
                    <span className="series-name">{series.name}</span>
                    <span className="series-count">{series.owned}/{series.total}</span>
                  </div>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{ width: `${series.percentage}%` }}
                    />
                  </div>
                  <div className="series-percentage">{series.percentage.toFixed(1)}%</div>
                </div>
              ))}
            </div>
          </div>

          {/* Rarity Distribution */}
          <div className="chart-container">
            <h3>Распределение по редкости</h3>
            <div className="rarity-distribution">
              {analytics.rarityStats.map((rarity, index) => (
                <div key={index} className="rarity-item">
                  <div className="rarity-header">
                    <span className="rarity-name">{rarity.name}</span>
                    <span className="rarity-count">{rarity.owned}/{rarity.total}</span>
                  </div>
                  <div className="rarity-bar">
                    <div 
                      className="rarity-fill"
                      style={{ 
                        width: `${rarity.percentage}%`,
                        backgroundColor: rarity.rarity === 'o' ? '#4CAF50' :
                                       rarity.rarity === 'ск' ? '#FF9800' : '#F44336'
                      }}
                    />
                  </div>
                  <div className="rarity-percentage">{rarity.percentage.toFixed(1)}%</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Top Cards Section */}
      <div className="top-cards-section">
        <h3>Самые ценные карточки в коллекции</h3>
        <div className="top-cards-grid">
          {analytics.topCards.map((card: any, index: number) => (
            <div key={index} className="top-card-item">
              <div className="card-rank">#{index + 1}</div>
              <div className="card-info">
                <div className="card-title">{card.card?.title}</div>
                <div className="card-number">#{card.card?.number}</div>
                <div className="card-rarity">
                  {card.card?.rarity === 'o' ? '🟢 Обычная' : 
                   card.card?.rarity === 'ск' ? '🟡 Необычная' : '🔴 Редкая'}
                </div>
              </div>
              <div className="card-value">
                <div className="value-amount">₽{card.value.toFixed(2)}</div>
                <div className="value-quantity">x{card.quantity}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Missing Cards by Series */}
      <div className="missing-cards-section">
        <h3>Отсутствующие карточки по сериям</h3>
        <div className="missing-series">
          {analytics.seriesStats.map((series, index) => {
            const missingInSeries = cardsData?.filter((card: any) => {
              const cardNumber = card.number;
              const isInRange = index === 0 ? (cardNumber >= 1 && cardNumber <= 275) :
                              index === 1 ? (cardNumber >= 276 && cardNumber <= 550) :
                              (cardNumber >= 551 && cardNumber <= 825);
              const isOwned = inventoryData?.some((item: any) => item.card?.id === card.id && item.has_card);
              return isInRange && !isOwned;
            }) || [];

            return (
              <div key={index} className="missing-series-item">
                <div className="missing-series-header">
                  <h4>{series.name}</h4>
                  <span className="missing-count">Отсутствует: {missingInSeries.length}</span>
                </div>
                <div className="missing-cards-list">
                  {missingInSeries.slice(0, 10).map((card: any) => (
                    <div key={card.id} className="missing-card">
                      <span className="card-number">#{card.number}</span>
                      <span className="card-title">{card.title}</span>
                      <span className="card-rarity">
                        {card.rarity === 'o' ? '🟢' : card.rarity === 'ск' ? '🟡' : '🔴'}
                      </span>
                    </div>
                  ))}
                  {missingInSeries.length > 10 && (
                    <div className="more-cards">... и еще {missingInSeries.length - 10} карточек</div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
