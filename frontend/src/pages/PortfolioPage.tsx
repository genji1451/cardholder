import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import apiClient from '../api/client';
import type { Card, InventoryItem } from '../api/types';
import './PortfolioPage.css';

const PortfolioPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  // const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  // Fetch cards data
  const { data: cardsData, isLoading: cardsLoading } = useQuery({
    queryKey: ['cards'],
    queryFn: async () => {
      const response = await apiClient.get('/cards/');
      return response.data.results || response.data;
    },
  });

  // Fetch inventory data
  const { data: inventoryData, isLoading: inventoryLoading } = useQuery({
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

  // Calculate portfolio stats
  const calculateStats = () => {
    if (!inventoryData || !cardsData) return null;

    const ownedCards = inventoryData.filter((item: InventoryItem) => item.has_card);
    const totalInvested = ownedCards.reduce((sum: number, item: InventoryItem) => 
      sum + (item.quantity * (item.card.base_price_rub || 0)), 0
    );
    
    const currentValue = ownedCards.reduce((sum: number, item: InventoryItem) => 
      sum + (item.quantity * (item.card.base_price_rub || 0)), 0
    );

    const profit = currentValue - totalInvested;
    const netProfit = profit; // Assuming no fees for now

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

  // Filter and search cards
  const filteredCards = cardsData?.filter((card: Card) => {
    const matchesSearch = card.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         card.number.toString().includes(searchTerm);
    
    if (selectedFilter === 'owned') {
      const inventoryItem = inventoryData?.find((item: InventoryItem) => 
        item.card_id === card.id && item.has_card
      );
      return matchesSearch && inventoryItem;
    } else if (selectedFilter === 'missing') {
      const inventoryItem = inventoryData?.find((item: InventoryItem) => 
        item.card_id === card.id && item.has_card
      );
      return matchesSearch && !inventoryItem;
    }
    
    return matchesSearch;
  }) || [];

  if (isLoading) {
    return (
      <div className="portfolio-page">
        <div className="loading">
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>🕸️</div>
          <p>Loading your portfolio...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="portfolio-page">
      {/* Header */}
      <div className="portfolio-header">
        <div className="header-left">
          <div className="logo-section">
            <div className="spider-logo">🕷️</div>
            <h1 className="portfolio-title">Spider-Man Cards Portfolio</h1>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-section">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">Invested</div>
            <div className="stat-value">₽{stats?.invested.toFixed(2) || '0.00'}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Current Value</div>
            <div className="stat-value">₽{stats?.currentValue.toFixed(2) || '0.00'}</div>
          </div>
          <div className="stat-card profit">
            <div className="stat-label">Profit</div>
            <div className="stat-value">₽{stats?.profit.toFixed(2) || '0.00'}</div>
          </div>
          <div className="stat-card profit">
            <div className="stat-label">Net Profit</div>
            <div className="stat-value">₽{stats?.netProfit.toFixed(2) || '0.00'}</div>
          </div>
        </div>
      </div>

      {/* Action Bar */}
      <div className="action-bar">
        <div className="search-section">
          <div className="search-input-container">
            <input
              type="text"
              placeholder="Add card to collection..."
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
            📊 All
          </button>
          <button 
            className={`filter-btn ${selectedFilter === 'owned' ? 'active' : ''}`}
            onClick={() => setSelectedFilter('owned')}
          >
            💼 Owned
          </button>
          <button 
            className={`filter-btn ${selectedFilter === 'missing' ? 'active' : ''}`}
            onClick={() => setSelectedFilter('missing')}
          >
            📥 Missing
          </button>
        </div>

        <div className="action-buttons">
          <button className="action-btn">
            <span className="new-badge">new</span>
            📤 Share
          </button>
          <button className="action-btn">
            <span className="new-badge">new</span>
            🔔 Alerts
          </button>
          <button className="action-btn">⚖️ Compare</button>
          <button className="action-btn">📈 ROI</button>
          <button className="action-btn">📤 Export</button>
          <button className="action-btn">📥 Import</button>
          <button className="action-btn">📚 Guide</button>
          <button className="action-btn">➕ Add</button>
          <button className="action-btn">⚙️ Settings</button>
        </div>
      </div>

      {/* Table Section */}
      <div className="table-section">
        <div className="table-header">
          <div className="table-search">
            <input
              type="text"
              placeholder="Search by name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="table-search-input"
            />
            <div className="search-icon">🔍</div>
          </div>
          <button className="percentage-btn">
            <span className="new-badge">new</span>
            %
          </button>
        </div>

        <div className="table-container">
          <table className="cards-table">
            <thead>
              <tr>
                <th>Icon</th>
                <th>Name</th>
                <th>Quantity</th>
                <th>Purchase Price</th>
                <th>Current Price</th>
                <th>Spent</th>
                <th>Status</th>
                <th>Difference</th>
                <th>Profit</th>
                <th>Net Profit</th>
              </tr>
            </thead>
            <tbody>
              {filteredCards.length === 0 ? (
                <tr>
                  <td colSpan={10} className="empty-state">
                    <div className="empty-content">
                      <div className="spider-logo">🕷️</div>
                      <p>No cards found</p>
                    </div>
                  </td>
                </tr>
              ) : (
                filteredCards.map((card: Card) => {
                  const inventoryItem = inventoryData?.find((item: InventoryItem) => 
                    item.card_id === card.id
                  );
                  
                  const isOwned = inventoryItem?.has_card || false;
                  const quantity = inventoryItem?.quantity || 0;
                  const spent = quantity * card.base_price_rub;
                  const currentValue = quantity * card.base_price_rub;
                  const profit = currentValue - spent;

                  return (
                    <tr key={card.id} className={isOwned ? 'owned' : 'missing'}>
                      <td>
                        <div className="card-icon">
                          {card.rarity === 'o' ? '🟢' : card.rarity === 'ск' ? '🟡' : '🔴'}
                        </div>
                      </td>
                      <td>
                        <div className="card-name">
                          <strong>{card.title}</strong>
                          <span className="card-number">#{card.number}</span>
                        </div>
                      </td>
                      <td>{quantity}</td>
                      <td>₽{card.base_price_rub.toFixed(2)}</td>
                      <td>₽{card.base_price_rub.toFixed(2)}</td>
                      <td>₽{spent.toFixed(2)}</td>
                      <td>
                        <span className={`status-badge ${isOwned ? 'owned' : 'missing'}`}>
                          {isOwned ? '✅ Owned' : '❌ Missing'}
                        </span>
                      </td>
                      <td className={profit >= 0 ? 'positive' : 'negative'}>
                        ₽{profit.toFixed(2)}
                      </td>
                      <td className={profit >= 0 ? 'positive' : 'negative'}>
                        ₽{profit.toFixed(2)}
                      </td>
                      <td className={profit >= 0 ? 'positive' : 'negative'}>
                        ₽{profit.toFixed(2)}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* <AddCardModal 
        isOpen={isAddModalOpen} 
        onClose={() => setIsAddModalOpen(false)} 
      /> */}
    </div>
  );
};

export default PortfolioPage;
