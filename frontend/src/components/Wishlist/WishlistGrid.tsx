import type { WishlistItem } from '../../api/types';
import './WishlistGrid.css';

interface WishlistGridProps {
  wishlist: WishlistItem[];
}

const WishlistGrid = ({ wishlist }: WishlistGridProps) => {
  const getPriorityColor = (priority: number) => {
    switch (priority) {
      case 3: return '#e53e3e'; // High - Red
      case 2: return '#ed8936'; // Medium - Orange
      case 1: return '#38a169'; // Low - Green
      default: return '#a0aec0';
    }
  };

  const getPriorityLabel = (priority: number) => {
    switch (priority) {
      case 3: return 'High Priority';
      case 2: return 'Medium Priority';
      case 1: return 'Low Priority';
      default: return 'Unknown';
    }
  };

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'o': return '#4299e1';
      case 'ск': return '#ed8936';
      case 'ук': return '#9f7aea';
      default: return '#a0aec0';
    }
  };

  const getRarityLabel = (rarity: string) => {
    switch (rarity) {
      case 'o': return 'Обычная';
      case 'ск': return 'Средняя карта';
      case 'ук': return 'Ультра карта';
      default: return rarity;
    }
  };

  return (
    <div className="wishlist-grid">
      {wishlist.map((item) => (
        <div key={item.id} className="wishlist-item">
          <div className="item-header">
            <div className="item-number">#{item.card.number}</div>
            <div 
              className="priority-badge"
              style={{ backgroundColor: getPriorityColor(item.priority) }}
            >
              {getPriorityLabel(item.priority)}
            </div>
          </div>
          
          <div className="item-content">
            <h3 className="item-title">{item.card.title}</h3>
            <p className="item-series">S{item.card.series}: {item.card.series_title}</p>
            
            <div className="item-details">
              <div className="detail-row">
                <span className="detail-label">Rarity:</span>
                <span 
                  className="detail-value rarity-badge"
                  style={{ backgroundColor: getRarityColor(item.card.rarity) }}
                >
                  {getRarityLabel(item.card.rarity)}
                </span>
              </div>
              
              {item.target_price_rub && (
                <div className="detail-row">
                  <span className="detail-label">Target Price:</span>
                  <span className="detail-value price">💰 {item.target_price_rub}₽</span>
                </div>
              )}
              
              <div className="detail-row">
                <span className="detail-label">Added:</span>
                <span className="detail-value date">
                  {new Date(item.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
            
            {item.note && (
              <p className="item-note">{item.note}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default WishlistGrid;
