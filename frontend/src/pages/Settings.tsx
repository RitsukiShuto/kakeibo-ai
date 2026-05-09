import React, { useEffect, useState } from 'react';
import { Settings as SettingsIcon, Save, AlertTriangle } from 'lucide-react';
import client from '../api/client';
import TopHeader from '../components/TopHeader';

const Settings: React.FC = () => {
  const [budget, setBudget] = useState('');
  const [profile, setProfile] = useState('');
  const [, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ text: string, type: 'success' | 'error' } | null>(null);

  const fetchSettings = async () => {
    setLoading(true);
    try {
      const [budgetRes, profileRes] = await Promise.all([
        client.get('/api/settings/budget'),
        client.get('/api/settings/profile')
      ]);
      setBudget(JSON.stringify(budgetRes.data, null, 2));
      setProfile(JSON.stringify(profileRes.data, null, 2));
    } catch (error) {
      console.error('Failed to fetch settings', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleSaveBudget = async () => {
    setSaving(true);
    setMessage(null);
    try {
      const data = JSON.parse(budget);
      await client.put('/api/settings/budget', data);
      setMessage({ text: '予算設定を保存しました', type: 'success' });
    } catch (error) {
      setMessage({ text: 'JSONの形式が正しくありません', type: 'error' });
    } finally {
      setSaving(false);
    }
  };

  const handleSaveProfile = async () => {
    setSaving(true);
    setMessage(null);
    try {
      const data = JSON.parse(profile);
      await client.put('/api/settings/profile', data);
      setMessage({ text: 'プロフィール設定を保存しました', type: 'success' });
    } catch (error) {
      setMessage({ text: 'JSONの形式が正しくありません', type: 'error' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <TopHeader title="システム設定" onRefresh={fetchSettings} />
      
      <div className="page-content">
        {message && (
          <div className={`review-summary mb-4 ${message.type === 'error' ? 'border-danger' : ''}`} 
               style={{ borderLeftColor: message.type === 'error' ? 'var(--danger)' : 'var(--success)' }}>
            {message.type === 'error' && <AlertTriangle size={16} className="text-danger inline mr-2" />}
            {message.text}
          </div>
        )}

        <div className="dashboard-grid" style={{ padding: 0 }}>
          {/* Budget Settings */}
          <div className="card section-budget" style={{ gridColumn: 'span 12' }}>
            <div className="card-header">
              <h3><SettingsIcon size={20} /> 予算設定 (budget.json)</h3>
              <button className="btn-primary" onClick={handleSaveBudget} disabled={saving}>
                <Save size={16} className="mr-2" /> 保存
              </button>
            </div>
            <div className="card-body">
              <textarea 
                className="form-control" 
                style={{ height: '400px', fontFamily: 'monospace', fontSize: '14px' }}
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
              />
            </div>
          </div>

          {/* Profile Settings */}
          <div className="card section-budget" style={{ gridColumn: 'span 12' }}>
            <div className="card-header">
              <h3><SettingsIcon size={20} /> AI ペルソナ設定 (profile.json)</h3>
              <button className="btn-primary" onClick={handleSaveProfile} disabled={saving}>
                <Save size={16} className="mr-2" /> 保存
              </button>
            </div>
            <div className="card-body">
              <textarea 
                className="form-control" 
                style={{ height: '300px', fontFamily: 'monospace', fontSize: '14px' }}
                value={profile}
                onChange={(e) => setProfile(e.target.value)}
              />
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Settings;
