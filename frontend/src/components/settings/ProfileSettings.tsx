import React from 'react';
import { User, Target, Wallet } from 'lucide-react';

interface ProfileSettingsProps {
  profile: any;
  updateProfileField: (path: string, value: any) => void;
}

const ProfileSettings: React.FC<ProfileSettingsProps> = ({ profile, updateProfileField }) => {
  const renderPolicyEditor = (obj: any, path: string = 'user.investment_policy') => {
    if (typeof obj !== 'object' || obj === null) {
      return (
        <input 
          type="text" 
          className="form-control" 
          style={{ background: 'rgba(0,0,0,0.3)' }}
          value={obj || ''} 
          onChange={(e) => {
            const val = e.target.value;
            const num = Number(val);
            updateProfileField(path, val === '' ? '' : (!isNaN(num) ? num : val));
          }}
        />
      );
    }
    
    return (
      <div style={{ marginLeft: path === 'user.investment_policy' ? 0 : '16px', borderLeft: path === 'user.investment_policy' ? 'none' : '2px solid rgba(59, 130, 246, 0.3)', paddingLeft: path === 'user.investment_policy' ? 0 : '16px', marginTop: path === 'user.investment_policy' ? 0 : '8px' }}>
        {Object.entries(obj).map(([key, val]) => (
          <div key={key} className="form-group mb-3">
            <label style={{ fontSize: '0.85rem', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              {typeof val === 'object' && val !== null ? <Wallet size={14} className="text-primary" /> : null}
              {key}
            </label>
            {renderPolicyEditor(val, `${path}.${key}`)}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="dashboard-grid" style={{ padding: 0 }}>
      <div className="card section-budget">
        <div className="card-header">
          <h3><User size={20} /> 基本情報</h3>
        </div>
        <div className="card-body">
          <div className="form-group">
            <label>お名前（または呼称）</label>
            <input 
              type="text" className="form-control" 
              value={profile?.user?.name || ''} 
              onChange={(e) => updateProfileField('user.name', e.target.value)} 
            />
          </div>
          <div className="form-group">
            <label>職業</label>
            <input 
              type="text" className="form-control" 
              value={profile?.user?.occupation || ''} 
              onChange={(e) => updateProfileField('user.occupation', e.target.value)} 
            />
          </div>
          <div className="form-group">
            <label>趣味 (カンマ区切り)</label>
            <input 
              type="text" className="form-control" 
              value={Array.isArray(profile?.user?.hobbies) ? profile.user.hobbies.join(', ') : (profile?.user?.hobbies || '')} 
              onChange={(e) => {
                const arr = e.target.value.split(',').map((s: string) => s.trim()).filter(Boolean);
                updateProfileField('user.hobbies', arr);
              }} 
            />
          </div>
          
          <div className="form-group mt-4">
            <label style={{ fontSize: '1.05rem', color: 'var(--primary)', borderBottom: '1px solid var(--border)', paddingBottom: '8px', marginBottom: '12px' }}>
              投資方針 (Investment Policy)
            </label>
            
            <div className="policy-editor-container" style={{ background: 'rgba(255,255,255,0.02)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border)' }}>
              {renderPolicyEditor(profile?.user?.investment_policy || {})}
            </div>
          </div>
        </div>
      </div>

      <div className="card section-ai-review">
        <div className="card-header">
          <h3><Target size={20} /> 目標設定</h3>
        </div>
        <div className="card-body">
          <div className="form-group">
            <label>目標日付</label>
            <input 
              type="date" className="form-control" 
              value={profile?.user?.target?.date || ''} 
              onChange={(e) => updateProfileField('user.target.date', e.target.value)} 
            />
          </div>
          <div className="form-group">
            <label>達成したいこと</label>
            <textarea 
              className="form-control" style={{ height: '150px' }}
              value={profile?.user?.target?.description || ''} 
              onChange={(e) => updateProfileField('user.target.description', e.target.value)} 
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileSettings;
