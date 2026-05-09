import React from 'react';
import { RefreshCcw, User } from 'lucide-react';

interface TopHeaderProps {
  title: string;
  onRefresh?: () => void;
}

const TopHeader: React.FC<TopHeaderProps> = ({ title, onRefresh }) => {
  return (
    <header className="top-header">
      <h1 className="page-title">{title}</h1>
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
