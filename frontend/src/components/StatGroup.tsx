import React from 'react';

interface StatProps {
  label: string;
  value: string;
  subValue?: string;
  colorClass?: string;
}

export const StatItem: React.FC<StatProps> = ({ label, value, subValue, colorClass }) => (
  <div className="flex flex-col">
    <span className="text-[10px] uppercase tracking-widest text-[var(--text-muted)] font-bold mb-3">{label}</span>
    <span className={`text-4xl font-black tracking-tighter leading-none ${colorClass || 'text-[var(--text-main)]'}`}>{value}</span>
    {subValue && <span className="text-xs font-semibold text-[var(--text-muted)] mt-3">{subValue}</span>}
  </div>
);

const StatGroup: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="grid grid-cols-1 md:grid-cols-3 gap-16 mb-20">
    {children}
  </div>
);

export default StatGroup;
