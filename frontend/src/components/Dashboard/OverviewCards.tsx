import type { AnalyticsOverview } from '../../api/types';
import './OverviewCards.css';

interface OverviewCardsProps {
  overview?: AnalyticsOverview;
}

const OverviewCards = ({ overview }: OverviewCardsProps) => {
  if (!overview) return null;

  const cards = [
    {
      title: 'Total Cards',
      value: overview.total_cards,
      icon: '📚',
      color: '#4299e1',
    },
    {
      title: 'Owned Cards',
      value: overview.owned_cards,
      icon: '✅',
      color: '#48bb78',
    },
    {
      title: 'Completion',
      value: `${overview.completion_percentage}%`,
      icon: '🎯',
      color: '#ed8936',
    },
    {
      title: 'Total Value',
      value: `${overview.total_value}₽`,
      icon: '💰',
      color: '#9f7aea',
    },
  ];

  return (
    <div className="overview-cards">
      <h2>Collection Overview</h2>
      <div className="cards-grid">
        {cards.map((card, index) => (
          <div key={index} className="overview-card" style={{ borderColor: card.color }}>
            <div className="card-icon" style={{ color: card.color }}>
              {card.icon}
            </div>
            <div className="card-content">
              <h3>{card.title}</h3>
              <p className="card-value">{card.value}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default OverviewCards;
