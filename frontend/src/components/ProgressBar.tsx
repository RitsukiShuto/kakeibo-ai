import React from 'react';

interface ProgressBarProps {
  label: string;
  actual: number;
  budget: number;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ label, actual, budget }) => {
  const percentage = budget > 0 ? Math.min((actual / budget) * 100, 100) : 0;
  const isWarning = percentage >= 80 && percentage < 100;
  const isDanger = percentage >= 100;

  return (
    <div className="progress-item">
      <div className="progress-info">
        <span>{label}</span>
        <span>{actual.toLocaleString()} / {budget.toLocaleString()} 円</span>
      </div>
      <div className="progress-bar-container">
        <div 
          className={`progress-bar ${isDanger ? 'danger' : isWarning ? 'warning' : ''}`} 
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

export default ProgressBar;
