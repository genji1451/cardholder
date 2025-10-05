import type { AnalyticsProgress } from '../../api/types';
import './ProgressChart.css';

interface ProgressChartProps {
  progress?: AnalyticsProgress;
}

const ProgressChart = ({ progress }: ProgressChartProps) => {
  if (!progress || !progress.series_progress.length) {
    return (
      <div className="progress-chart">
        <h2>Series Progress</h2>
        <div className="no-data">No series data available</div>
      </div>
    );
  }

  return (
    <div className="progress-chart">
      <h2>Series Progress</h2>
      <div className="progress-list">
        {progress.series_progress.map((series) => (
          <div key={series.series_id} className="progress-item">
            <div className="progress-header">
              <h3>S{series.series_number}: {series.series_title}</h3>
              <div className="progress-percentage">
                {series.percentage}%
              </div>
            </div>
            
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ 
                  width: `${series.percentage}%`,
                  backgroundColor: series.percentage >= 80 ? '#38a169' :
                                 series.percentage >= 50 ? '#ed8936' : '#e53e3e'
                }}
              />
            </div>
            
            <div className="progress-details">
              <span className="progress-count">
                {series.owned} / {series.total} cards
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProgressChart;
