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
    <div className="flex flex-col gap-2">
      <div className="flex justify-between items-end">
        <span className="font-bold text-sm text-slate-200">{label}</span>
        <div className="text-right">
          <span className="text-sm font-black text-slate-100">¥{actual.toLocaleString()}</span>
          <span className="text-[10px] font-bold text-slate-500 ml-1">/ ¥{budget.toLocaleString()}</span>
          {showDiff && paceLimit !== undefined && (
            <div className={`text-[10px] font-black tracking-tight ${diff <= 0 ? 'text-emerald-500' : 'text-red-500'}`}>
              {diff > 0 ? '+' : '-'}¥{Math.abs(diff).toLocaleString()}
            </div>
          )}
        </div>
      </div>
      <div className="relative h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
        <div 
          className={`h-full rounded-full transition-all duration-700 ease-out ${
            isOverPace ? 'bg-amber-500' : 'bg-indigo-500'
          }`} 
          style={{ width: `${percentage}%` }}
        />
        {pacePercentage !== null && (
          <div 
            className="absolute top-0 w-0.5 h-full bg-amber-500 z-10 shadow-[0_0_8px_rgba(245,158,11,0.6)]" 
            style={{ left: `${pacePercentage}%` }}
            title="Pace Limit"
          />
        )}
      </div>
    </div>
  );
};

export default ProgressBar;
