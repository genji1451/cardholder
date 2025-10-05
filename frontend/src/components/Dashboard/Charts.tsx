import { useQuery } from '@tanstack/react-query';
import apiClient from '../../api/client';
import type { AnalyticsDistribution } from '../../api/types';
import './Charts.css';

const Charts = () => {
  const { data: distribution } = useQuery<AnalyticsDistribution>({
    queryKey: ['analytics', 'distribution'],
    queryFn: async () => {
      const response = await apiClient.get('/analytics/distribution/');
      return response.data;
    },
  });

  if (!distribution) return null;

  return (
    <div className="charts">
      <h2>Collection Distribution</h2>
      <div className="charts-grid">
        <div className="chart-container">
          <h3>By Rarity</h3>
          <div className="rarity-chart">
            {distribution.rarity.map((item, index) => (
              <div key={index} className="rarity-item">
                <div className="rarity-label">
                  {item.card__rarity === 'o' ? 'Обычная' :
                   item.card__rarity === 'ск' ? 'Средняя карта' : 'Ультра карта'}
                </div>
                <div className="rarity-bar">
                  <div 
                    className="rarity-fill"
                    style={{ 
                      width: `${(item.count / Math.max(...distribution.rarity.map(r => r.count))) * 100}%`,
                      backgroundColor: item.card__rarity === 'o' ? '#4299e1' :
                                     item.card__rarity === 'ск' ? '#ed8936' : '#9f7aea'
                    }}
                  />
                </div>
                <div className="rarity-count">{item.count}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="chart-container">
          <h3>By Series</h3>
          <div className="series-chart">
            {distribution.series.map((item, index) => (
              <div key={index} className="series-item">
                <div className="series-label">
                  S{item.card__series__number}: {item.card__series__title}
                </div>
                <div className="series-bar">
                  <div 
                    className="series-fill"
                    style={{ 
                      width: `${(item.count / Math.max(...distribution.series.map(s => s.count))) * 100}%`,
                      backgroundColor: `hsl(${index * 60}, 70%, 50%)`
                    }}
                  />
                </div>
                <div className="series-count">{item.count}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Charts;
