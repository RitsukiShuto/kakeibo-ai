import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, ListTodo, Bot, Handshake, Settings } from 'lucide-react';

const Sidebar: React.FC = () => {
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
    </aside>
  );
};

export default Sidebar;
