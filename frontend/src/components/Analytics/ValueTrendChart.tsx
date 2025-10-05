import type { AnalyticsValueTrend } from '../../api/types';
import './ValueTrendChart.css';

interface ValueTrendChartProps {
  valueTrend?: AnalyticsValueTrend;
}

const ValueTrendChart = ({ valueTrend }: ValueTrendChartProps) => {
  if (!valueTrend || !valueTrend.value_trend.length) {
    return (
      <div className="value-trend-chart">
        <h2>Value Trend</h2>
        <div className="no-data">No spending data available</div>
      </div>
    );
  }

  const maxSpent = Math.max(...valueTrend.value_trend.map(point => point.total_spent));

  return (
    <div className="value-trend-chart">
      <h2>Monthly Spending Trend</h2>
      <div className="trend-chart">
        {valueTrend.value_trend.map((point, index) => (
          <div key={index} className="trend-item">
            <div className="trend-month">
              {new Date(point.month).toLocaleDateString('en-US', { 
                month: 'short', 
                year: 'numeric' 
              })}
            </div>
            <div className="trend-bar">
              <div 
                className="trend-fill"
                style={{ 
                  width: `${(point.total_spent / maxSpent) * 100}%`,
                  backgroundColor: '#4299e1'
                }}
              />
            </div>
            <div className="trend-values">
              <div className="trend-spent">{point.total_spent}₽</div>
              <div className="trend-avg">Avg: {point.avg_price}₽</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ValueTrendChart;
