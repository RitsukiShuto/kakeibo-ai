import React, { useEffect, useState } from 'react';
import { Settings as SettingsIcon, Save, AlertTriangle, Bot } from 'lucide-react';
import client from '../api/client';
import type { AISettings, AIModel } from '../api/client';
import TopHeader from '../components/TopHeader';

const Settings: React.FC = () => {
  const [budget, setBudget] = useState('');
  const [profile, setProfile] = useState('');
  const [aiSettings, setAiSettings] = useState<AISettings | null>(null);
  const [, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ text: string, type: 'success' | 'error' } | null>(null);

  const fetchSettings = async () => {
    setLoading(true);
    try {
      const [budgetRes, profileRes, aiRes] = await Promise.all([
        client.get('/api/settings/budget'),
        client.get('/api/settings/profile'),
        client.get<AISettings>('/api/settings/ai-models')
      ]);
      setBudget(JSON.stringify(budgetRes.data, null, 2));
      setProfile(JSON.stringify(profileRes.data, null, 2));
      setAiSettings(aiRes.data);
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

  const handleModelChange = async (modelId: string) => {
    setSaving(true);
    try {
      await client.put('/api/settings/active-model', { active_model: modelId });
      setAiSettings(prev => prev ? { ...prev, active_model: modelId } : null);
      setMessage({ text: 'AIモデルを変更しました', type: 'success' });
    } catch (error) {
      console.error('Failed to change model', error);
      setMessage({ text: 'モデルの変更に失敗しました', type: 'error' });
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
          {/* AI Model Selection */}
          <div className="card section-budget" style={{ gridColumn: 'span 12' }}>
            <div className="card-header">
              <h3><Bot size={20} /> AI モデル設定</h3>
            </div>
            <div className="card-body">
              <div className="flex flex-col gap-4">
                <p className="text-muted text-sm">家計簿の分析に使用するAIモデルを選択してください。</p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {aiSettings?.available_models.map((model: AIModel) => (
                    <div 
                      key={model.id} 
                      className={`p-4 border rounded-lg cursor-pointer transition-all ${aiSettings.active_model === model.id ? 'border-primary bg-primary-light' : 'hover:border-gray-400'}`}
                      style={{ 
                        borderColor: aiSettings.active_model === model.id ? 'var(--primary)' : 'var(--border-color)',
                        backgroundColor: aiSettings.active_model === model.id ? 'rgba(134, 59, 255, 0.1)' : 'transparent'
                      }}
                      onClick={() => handleModelChange(model.id)}
                    >
                      <div className="font-bold mb-1">{model.name}</div>
                      <div className="text-xs text-muted">{model.description}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

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
