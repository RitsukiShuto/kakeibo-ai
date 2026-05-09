import React, { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, ListTodo, Bot, Handshake, Settings, Circle } from 'lucide-react';
import client from '../api/client';

interface SystemStatus {
  services: {
    slack: {
      status: 'online' | 'offline';
      last_heartbeat: string | null;
    };
  };
}

const Sidebar: React.FC = () => {
  const [status, setStatus] = useState<'online' | 'offline' | 'loading'>('loading');

  const fetchStatus = async () => {
    try {
      const res = await client.get<SystemStatus>('/api/status');
      setStatus(res.data.services.slack.status);
    } catch (error) {
      console.error('Failed to fetch system status', error);
      setStatus('offline');
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000); // 30秒ごとに更新
    return () => clearInterval(interval);
  }, []);

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <LayoutDashboard size={24} style={{ marginRight: '8px', color: 'var(--primary)', verticalAlign: 'middle' }} />
        <span>Kakeibo AI</span>
      </div>
      <nav className="sidebar-nav">
        <ul>
          <li>
            <NavLink to="/" className={({ isActive }) => (isActive ? 'active' : '')}>
              <LayoutDashboard size={20} />
              <span>ダッシュボード</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/transactions" className={({ isActive }) => (isActive ? 'active' : '')}>
              <ListTodo size={20} />
              <span>明細一覧</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/ai-review" className={({ isActive }) => (isActive ? 'active' : '')}>
              <Bot size={20} />
              <span>AIレビュー</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/expense-splitter" className={({ isActive }) => (isActive ? 'active' : '')}>
              <Handshake size={20} />
              <span>立替・精算</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/settings" className={({ isActive }) => (isActive ? 'active' : '')}>
              <Settings size={20} />
              <span>設定</span>
            </NavLink>
          </li>
        </ul>
      </nav>
      
      <div className="sidebar-footer" style={{ padding: '20px', borderTop: '1px solid var(--border-color)', marginTop: 'auto' }}>
        <div className="flex items-center text-sm" style={{ color: 'var(--text-muted)' }}>
          <Circle 
            size={10} 
            fill={status === 'online' ? '#10b981' : (status === 'loading' ? '#f59e0b' : '#ef4444')} 
            color="transparent" 
            style={{ marginRight: '8px' }} 
          />
          <span>Slack Bot: {status === 'online' ? 'Online' : (status === 'loading' ? 'Checking...' : 'Offline')}</span>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
