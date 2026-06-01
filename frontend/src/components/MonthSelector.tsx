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
    <div className="flex items-center gap-3 bg-indigo-50 px-4 py-2 rounded-full">
      <button onClick={handlePrev} className="text-indigo-600 font-bold hover:opacity-70">◀</button>
      <span className="text-indigo-600 font-bold text-sm min-w-[90px] text-center">
        {year}年 {month}月
      </span>
      <button onClick={handleNext} className="text-indigo-600 font-bold hover:opacity-70">▶</button>
    </div>
  );
};

export default MonthSelector;
