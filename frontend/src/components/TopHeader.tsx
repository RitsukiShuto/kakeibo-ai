import React from 'react';
import { RefreshCcw, User } from 'lucide-react';

interface TopHeaderProps {
  title: string;
  onRefresh?: () => void;
  timeframes?: string[];
  activeTimeframe?: string;
  onTimeframeChange?: (tf: string) => void;
}

const TopHeader: React.FC<TopHeaderProps> = ({ 
  title, 
  onRefresh, 
  timeframes = [], 
  activeTimeframe, 
  onTimeframeChange 
}) => {
  const tfLabels: Record<string, string> = {
    daily: '日次',
    weekly: '週次',
    monthly: '月次',
    yearly: '年次'
  };

  return (
    <header className="top-header">
      <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
        <h1 className="page-title" style={{ margin: 0 }}>{title}</h1>
        
        {timeframes.length > 0 && (
          <div className="timeframe-tabs" style={{ display: 'flex', gap: '0.5rem' }}>
            {timeframes.map((tf) => (
              <button
                key={tf}
                className={`tab-btn ${activeTimeframe === tf ? 'active' : ''}`}
                onClick={() => onTimeframeChange?.(tf)}
              >
                {tfLabels[tf] || tf}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="header-actions">
        <button className="btn-refresh" onClick={onRefresh}>
          <RefreshCcw size={16} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
          <span>更新</span>
        </button>
        <div className="user-profile">
          <User size={24} />
        </div>
      </div>
    </header>
  );
};

export default TopHeader;
