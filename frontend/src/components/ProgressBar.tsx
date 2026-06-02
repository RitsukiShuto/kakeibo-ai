import React from 'react';

interface ProgressBarProps {
  label: string;
  actual: number;
  budget: number;
  paceLimit?: number; // 今日の理想ライン
  showDiff?: boolean;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ label, actual, budget, paceLimit, showDiff }) => {
  const percentage = budget > 0 ? Math.min((actual / budget) * 100, 100) : 0;
  const pacePercentage = (paceLimit && budget > 0) ? (paceLimit / budget) * 100 : null;
  
  // ペースとの乖離 (負が節約、正が超過)
  const diff = paceLimit !== undefined ? actual - paceLimit : 0;
  const isOverPace = paceLimit !== undefined && actual > paceLimit;

  return (
    <div className="progress-item">
      <div className="progress-info items-baseline">
        <span className="font-bold text-lg text-[var(--text-main)]">{label}</span>
        <span className="text-sm font-medium text-[var(--text-muted)]">
          <b className="text-[var(--text-main)]">¥{actual.toLocaleString()}</b>
          {showDiff && paceLimit !== undefined && (
            <span className={diff <= 0 ? 'text-[var(--success)] ml-2' : 'text-[var(--danger)] ml-2'}>
              ({diff > 0 ? '+' : ''}¥{Math.abs(diff).toLocaleString()})
            </span>
          )}
          {" / ¥"}{budget.toLocaleString()}
        </span>
      </div>
      <div className="progress-bar-container relative">
        <div 
          className={`progress-bar ${isOverPace ? 'warning' : ''}`} 
          style={{ width: `${percentage}%` }}
        />
        {pacePercentage !== null && (
          <div 
            className="pace-marker absolute top-0 w-0.5 h-full bg-[var(--warning)] z-10" 
            style={{ left: `${pacePercentage}%`, boxShadow: '0 0 8px rgba(245, 158, 11, 0.5)' }}
          />
        )}
      </div>
    </div>
  );
};

export default ProgressBar;
