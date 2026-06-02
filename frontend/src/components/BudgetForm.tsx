import React from 'react';

interface BudgetFormProps {
  history: string[]; // e.g. ["W", "L", "W", "W"]
}

const BudgetForm: React.FC<BudgetFormProps> = ({ history }) => {
  if (!history || history.length === 0) {
    return null;
  }

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs font-bold text-slate-400 mr-2">直近の成績:</span>
      {history.map((result, index) => {
        const isCurrent = index === 0;
        let bgColor = 'bg-slate-200';
        let textColor = 'text-slate-500';
        let borderColor = 'border-transparent';

        if (result === 'W') {
          bgColor = 'bg-emerald-100';
          textColor = 'text-emerald-700';
          borderColor = isCurrent ? 'border-emerald-500' : 'border-transparent';
        } else if (result === 'L') {
          bgColor = 'bg-rose-100';
          textColor = 'text-rose-700';
          borderColor = isCurrent ? 'border-rose-500' : 'border-transparent';
        } else if (result === 'D') {
          bgColor = 'bg-amber-100';
          textColor = 'text-amber-700';
          borderColor = isCurrent ? 'border-amber-500' : 'border-transparent';
        }

        return (
          <div 
            key={index}
            className={`w-8 h-8 rounded-full flex items-center justify-center font-black text-sm border-2 ${bgColor} ${textColor} ${borderColor}`}
            title={isCurrent ? "今週" : `${index}週前`}
          >
            {result}
          </div>
        );
      })}
    </div>
  );
};

export default BudgetForm;
