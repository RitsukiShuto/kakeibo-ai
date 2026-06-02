import React from 'react';

interface MonthSelectorProps {
  currentMonth: string; // YYYY-MM
  onChange: (newMonth: string) => void;
}

const MonthSelector: React.FC<MonthSelectorProps> = ({ currentMonth, onChange }) => {
  const [year, month] = currentMonth.split('-').map(Number);
  
  const handlePrev = () => {
    const d = new Date(year, month - 2);
    onChange(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`);
  };

  const handleNext = () => {
    const d = new Date(year, month);
    onChange(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`);
  };

  return (
    <div className="flex items-center gap-3 bg-[rgba(0,0,0,0.2)] border border-[var(--border)] px-4 py-1.5 rounded-xl shadow-sm">
      <button 
        onClick={handlePrev} 
        className="text-[var(--primary-light)] font-bold hover:text-[var(--primary)] transition-colors p-1"
      >
        ◀
      </button>
      <span className="text-[var(--text-main)] font-bold text-sm min-w-[100px] text-center">
        {year}年 {month}月
      </span>
      <button 
        onClick={handleNext} 
        className="text-[var(--primary-light)] font-bold hover:text-[var(--primary)] transition-colors p-1"
      >
        ▶
      </button>
    </div>
  );
};

export default MonthSelector;
