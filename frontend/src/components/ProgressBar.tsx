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
    <div className="progress-item mb-10">
      <div className="flex justify-between items-baseline mb-3">
        <span className="font-bold text-lg">{label}</span>
        <span className="text-sm font-medium text-slate-500">
          <b className="text-slate-900">¥{actual.toLocaleString()}</b>
          {showDiff && paceLimit !== undefined && (
            <span className={diff <= 0 ? 'text-emerald-500 ml-2' : 'text-rose-500 ml-2'}>
              ({diff > 0 ? '+' : ''}¥{Math.abs(diff).toLocaleString()})
            </span>
          )}
          {" / ¥"}{budget.toLocaleString()}
        </span>
      </div>
      <div className="h-2.5 bg-slate-100 rounded-full relative">
        <div 
          className={`progress-bar h-full rounded-full transition-all duration-500 ${isOverPace ? 'bg-amber-500' : 'bg-indigo-600'}`} 
          style={{ width: `${percentage}%` }}
        />
        {pacePercentage !== null && (
          <div 
            className="pace-marker absolute top-[-5px] w-0.5 h-5 bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]" 
            style={{ left: `${pacePercentage}%` }}
          />
        )}
      </div>
    </div>
  );
};

export default ProgressBar;
