import React from 'react';

interface KPICardProps {
  title: string;
  value: string;
  trend?: string;
  trendType?: 'positive' | 'negative';
}

const KPICard: React.FC<KPICardProps> = ({ title, value, trend, trendType }) => {
  return (
    <div className="card kpi-card">
      <div className="kpi-title">{title}</div>
      <div className="kpi-value">{value}</div>
      {trend && (
        <div className={`kpi-trend ${trendType === 'positive' ? 'positive' : 'negative'}`}>
          {trend}
        </div>
      )}
    </div>
  );
};

export default KPICard;
