import React from 'react';
import ProgressBar from './ProgressBar';
import type { BudgetActual } from '../api/client';

interface BudgetPacemakerProps {
  timeframe: string;
  onTimeframeChange: (tf: string) => void;
  variableExpenses: BudgetActual[];
  fixedExpenses: BudgetActual[];
}

const timeframes = [
  { id: 'weekly', label: '週次' },
  { id: 'monthly', label: '月次' },
  { id: 'quarterly', label: '四半期' },
  { id: 'yearly', label: '年次' }
];

const BudgetPacemaker: React.FC<BudgetPacemakerProps> = ({ timeframe, onTimeframeChange, variableExpenses, fixedExpenses }) => {
  return (
    <div className="budget-pacemaker">
      <div className="flex gap-1 mb-8 border-b border-slate-100 pb-2">
        {timeframes.map(t => (
          <button 
            key={t.id} 
            onClick={() => onTimeframeChange(t.id)}
            className={`px-6 py-2 text-xs font-black rounded-md transition-colors ${timeframe === t.id ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:bg-slate-50'}`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="mb-16">
        <h2 className="text-lg font-black mb-10 flex items-center gap-4 text-slate-400 uppercase tracking-widest">
          変動費の予実管理 
          <div className="flex-1 h-px bg-slate-100"></div>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-16 gap-y-2">
          {variableExpenses.length > 0 ? (
            variableExpenses.map(item => (
              <ProgressBar 
                key={item.category}
                label={item.category}
                actual={item.actual}
                budget={item.budget}
                paceLimit={item.pace_limit}
                showDiff={true}
              />
            ))
          ) : (
            <div className="text-slate-400 font-medium">データがありません。</div>
          )}
        </div>
      </div>

      <div>
        <h2 className="text-lg font-black mb-10 flex items-center gap-4 text-slate-400 uppercase tracking-widest">
          固定費の状況 
          <div className="flex-1 h-px bg-slate-100"></div>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-16 gap-y-2">
          {fixedExpenses.length > 0 ? (
            fixedExpenses.map(item => (
              <ProgressBar 
                key={item.category}
                label={item.category}
                actual={item.actual}
                budget={item.budget}
              />
            ))
          ) : (
            <div className="text-slate-400 font-medium">データがありません。</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BudgetPacemaker;
