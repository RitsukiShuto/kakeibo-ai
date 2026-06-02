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
  { id: 'weekly', label: 'WEEKLY' },
  { id: 'monthly', label: 'MONTHLY' },
  { id: 'quarterly', label: 'QUARTERLY' },
  { id: 'yearly', label: 'YEARLY' }
];

const BudgetPacemaker: React.FC<BudgetPacemakerProps> = ({ timeframe, onTimeframeChange, variableExpenses, fixedExpenses }) => {
  return (
    <div className="budget-pacemaker">
      <div className="flex flex-wrap gap-2 mb-12">
        {timeframes.map(t => (
          <button 
            key={t.id} 
            onClick={() => onTimeframeChange(t.id)}
            className={`px-4 py-2 rounded-full text-[10px] font-black tracking-widest transition-all ${
              timeframe === t.id 
                ? 'bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/20' 
                : 'bg-slate-800/50 text-slate-500 hover:text-slate-300 hover:bg-slate-800'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="mb-16">
        <div className="flex items-center gap-4 mb-8">
          <h2 className="text-xs font-black text-slate-500 uppercase tracking-[0.2em] whitespace-nowrap">
            Variable Expenses
          </h2>
          <div className="flex-1 h-px bg-slate-800/50"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-16 gap-y-6">
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
            <div className="col-span-2 text-slate-500 text-sm font-medium py-4">
              データがありません。
            </div>
          )}
        </div>
      </div>

      <div>
        <div className="flex items-center gap-4 mb-8">
          <h2 className="text-xs font-black text-slate-500 uppercase tracking-[0.2em] whitespace-nowrap">
            Fixed Expenses
          </h2>
          <div className="flex-1 h-px bg-slate-800/50"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-16 gap-y-6">
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
            <div className="col-span-2 text-slate-500 text-sm font-medium py-4">
              データがありません。
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BudgetPacemaker;
