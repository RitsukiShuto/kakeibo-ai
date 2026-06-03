import React from 'react';
import type { WeeklyFormItem } from '../api/client';

interface WeeklyFormProps {
  history: WeeklyFormItem[];
  selectedWeek?: string;
  onWeekClick?: (startDate: string) => void;
}

const WeeklyForm: React.FC<WeeklyFormProps> = ({ history, selectedWeek, onWeekClick }) => {
  if (!history || history.length === 0) {
    return null;
  }

  // API returns [3 weeks ago, 2 weeks ago, 1 week ago, current week]
  // We want to show them in chronological order? Or as is?
  // Previous code showed index 0 as "Current".
  // Looking at src/api/routers/analysis.py: i in range(3, -1, -1) -> [3, 2, 1, 0]
  // So results[0] is 3 weeks ago, results[3] is current week.
  
  return (
    <div className="flex items-center gap-2">
      <span className="text-[10px] font-black text-slate-500 mr-3 uppercase tracking-[0.2em]">Weekly Form:</span>
      <div className="flex gap-2">
        {history.map((item, index) => {
          const isCurrent = index === history.length - 1;
          const isSelected = selectedWeek === item.start_date;
          const result = item.status;

          let bgColor = 'rgba(255, 255, 255, 0.05)';
          let textColor = '#64748b'; // slate-500
          let borderColor = isSelected ? 'rgba(255, 255, 255, 0.5)' : 'transparent';
          let shadow = 'none';

          if (result === 'W') {
            bgColor = 'rgba(16, 185, 129, 0.1)';
            textColor = '#34d399'; // emerald-400
            if (isCurrent || isSelected) {
              borderColor = '#10b981'; // emerald-500
              shadow = isSelected ? '0 0 16px rgba(16, 185, 129, 0.6)' : '0 0 12px rgba(16, 185, 129, 0.4)';
            }
          } else if (result === 'L') {
            bgColor = 'rgba(239, 68, 68, 0.1)';
            textColor = '#f87171'; // red-400
            if (isCurrent || isSelected) {
              borderColor = '#ef4444'; // red-500
              shadow = isSelected ? '0 0 16px rgba(239, 68, 68, 0.6)' : '0 0 12px rgba(239, 68, 68, 0.4)';
            }
          } else if (result === 'D') {
            bgColor = 'rgba(245, 158, 11, 0.1)';
            textColor = '#fbbf24'; // amber-400
            if (isCurrent || isSelected) {
              borderColor = '#f59e0b'; // amber-500
              shadow = isSelected ? '0 0 16px rgba(245, 158, 11, 0.6)' : '0 0 12px rgba(245, 158, 11, 0.4)';
            }
          }

          return (
            <button 
              key={index}
              onClick={() => onWeekClick?.(item.start_date)}
              className={`w-9 h-9 rounded-lg flex items-center justify-center font-black text-xs border-2 transition-all duration-300 relative hover:scale-110 active:scale-95`}
              style={{ 
                backgroundColor: bgColor, 
                color: textColor, 
                borderColor: borderColor,
                boxShadow: shadow,
                opacity: isCurrent || isSelected ? 1 : 0.4
              }}
              title={`${item.start_date} ~ ${item.end_date}`}
            >
              {result}
              {isCurrent && !isSelected && (
                <span className="absolute -top-1 -right-1 flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" style={{ backgroundColor: borderColor }}></span>
                  <span className="relative inline-flex rounded-full h-2 w-2" style={{ backgroundColor: borderColor }}></span>
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default WeeklyForm;
