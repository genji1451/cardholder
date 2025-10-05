import type { AnalyticsOverview } from '../../api/types';
import './TopExpensive.css';

interface TopExpensiveProps {
  overview?: AnalyticsOverview;
}

const TopExpensive = ({ overview }: TopExpensiveProps) => {
  if (!overview || !overview.recent_trades.length) {
    return (
      <div className="top-expensive">
        <h2>Recent Purchases</h2>
        <div className="no-data">No recent purchases</div>
      </div>
    );
  }

  return (
    <div className="top-expensive">
      <h2>Recent Purchases</h2>
      <div className="trades-list">
        {overview.recent_trades.map((trade, index) => (
          <div key={index} className="trade-item">
            <div className="trade-info">
              <h4>{trade.card_title}</h4>
              <p className="trade-details">
                {trade.quantity}x • {trade.price}₽
              </p>
            </div>
            <div className="trade-date">
              {new Date(trade.date).toLocaleDateString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TopExpensive;
