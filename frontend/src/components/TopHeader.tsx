import React from 'react';
import { RefreshCcw, User } from 'lucide-react';

interface TopHeaderProps {
  title: string;
  onRefresh?: () => void;
  timeframes?: string[];
  activeTimeframe?: string;
  onTimeframeChange?: (tf: string) => void;
  loading?: boolean;
}

const TopHeader: React.FC<TopHeaderProps> = ({ 
  title, 
  onRefresh, 
  timeframes = [], 
  activeTimeframe, 
  onTimeframeChange,
  loading = false
}) => {
  const tfLabels: Record<string, string> = {
    daily: '日次',
    weekly: '週次',
    monthly: '月次',
    yearly: '年次'
  };

  return (
    <header className="top-header">
      <div className="flex items-center gap-4 sm:gap-8 flex-wrap">
        <h1 className="page-title">{title}</h1>
        
        {timeframes.length > 0 && (
          <div className="timeframe-tabs">
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
        <button className="btn-refresh" onClick={onRefresh} disabled={loading}>
          <RefreshCcw 
            size={16} 
            className={loading ? 'animate-spin' : ''}
            style={{ marginRight: '8px' }}
          />
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
