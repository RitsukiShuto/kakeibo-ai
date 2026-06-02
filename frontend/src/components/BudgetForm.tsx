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
      <span className="text-xs font-bold text-[var(--text-muted)] mr-2 uppercase tracking-wider">直近の成績:</span>
      {history.map((result, index) => {
        const isCurrent = index === 0;
        let bgColor = 'rgba(255, 255, 255, 0.05)';
        let textColor = 'var(--text-muted)';
        let borderColor = 'transparent';

        if (result === 'W') {
          bgColor = 'rgba(16, 185, 129, 0.15)';
          textColor = '#34d399';
          borderColor = isCurrent ? '#10b981' : 'transparent';
        } else if (result === 'L') {
          bgColor = 'rgba(239, 68, 68, 0.15)';
          textColor = '#f87171';
          borderColor = isCurrent ? '#ef4444' : 'transparent';
        } else if (result === 'D') {
          bgColor = 'rgba(245, 158, 11, 0.15)';
          textColor = '#fbbf24';
          borderColor = isCurrent ? '#f59e0b' : 'transparent';
        }

        return (
          <div 
            key={index}
            className={`w-8 h-8 rounded-full flex items-center justify-center font-black text-xs border-2 transition-all`}
            style={{ 
              backgroundColor: bgColor, 
              color: textColor, 
              borderColor: borderColor,
              opacity: isCurrent ? 1 : 0.7
            }}
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
