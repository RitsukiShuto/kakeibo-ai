import React from 'react';
import { CheckCircle2, User, Heart, Shield, Terminal, Zap } from 'lucide-react';

interface PersonaCardProps {
  id: string;
  name: string;
  description: string;
  isActive: boolean;
  onClick: () => void;
}

const PersonaCard: React.FC<PersonaCardProps> = ({ id, name, description, isActive, onClick }) => {
  const getIcon = () => {
    switch (id) {
      case 'gal':
        return <Zap size={32} className={isActive ? 'text-primary' : 'text-muted'} />;
      case 'butler':
        return <Shield size={32} className={isActive ? 'text-primary' : 'text-muted'} />;
      case 'zen':
        return <Heart size={32} className={isActive ? 'text-primary' : 'text-muted'} />;
      case 'sergeant':
        return <Terminal size={32} className={isActive ? 'text-primary' : 'text-muted'} />;
      default:
        return <User size={32} className={isActive ? 'text-primary' : 'text-muted'} />;
    }
  };

  const getEmoji = () => {
    switch (id) {
      case 'gal': return '✨';
      case 'butler': return '🤵';
      case 'zen': return '🌿';
      case 'sergeant': return '🎖️';
      default: return '🤖';
    }
  };

  return (
    <div 
      className={`persona-card ${isActive ? 'active' : ''}`}
      onClick={onClick}
    >
      <div className="persona-emoji">{getEmoji()}</div>
      <div className="persona-content">
        <div className="persona-header">
          <div className="persona-name">{name}</div>
          {isActive && <CheckCircle2 size={20} className="text-primary" />}
        </div>
        <div className="persona-desc">{description}</div>
      </div>

      <style>{`
        .persona-card {
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid var(--border);
          border-radius: 16px;
          padding: 1.5rem;
          cursor: pointer;
          transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
          display: flex;
          align-items: center;
          gap: 1.5rem;
          position: relative;
          overflow: hidden;
        }
        .persona-card:hover {
          border-color: var(--primary);
          background: rgba(255, 255, 255, 0.05);
          transform: translateY(-2px);
        }
        .persona-card.active {
          border-color: var(--primary);
          background: rgba(59, 130, 246, 0.08);
          box-shadow: 0 0 0 1px var(--primary);
        }
        .persona-emoji {
          font-size: 3rem;
          line-height: 1;
          filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
        }
        .persona-content {
          flex: 1;
        }
        .persona-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }
        .persona-name {
          font-weight: 800;
          font-size: 1.25rem;
          color: var(--text-main);
        }
        .persona-desc {
          font-size: 0.9rem;
          color: var(--text-muted);
          line-height: 1.4;
        }
      `}</style>
    </div>
  );
};

export default PersonaCard;
