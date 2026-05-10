import React, { useEffect, useState } from 'react';
import { Settings as SettingsIcon, Save, AlertTriangle, Bot, User, Target, Wallet, Code } from 'lucide-react';
import client from '../api/client';
import type { AISettings, AIModel } from '../api/client';
import TopHeader from '../components/TopHeader';

const Settings: React.FC = () => {
  const [budget, setBudget] = useState<any>(null);
  const [profile, setProfile] = useState<any>(null);
  const [aiSettings, setAiSettings] = useState<AISettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<'ui' | 'json'>('ui');
  const [message, setMessage] = useState<{ text: string, type: 'success' | 'error' } | null>(null);

  // JSON string states for the 'Advanced' tab
  const [budgetJson, setBudgetJson] = useState('');
  const [profileJson, setProfileJson] = useState('');

  const fetchSettings = async () => {
    setLoading(true);
    try {
      const [budgetRes, profileRes, aiRes] = await Promise.all([
        client.get('/api/settings/budget'),
        client.get('/api/settings/profile'),
        client.get<AISettings>('/api/settings/ai-models')
      ]);
      
      setBudget(budgetRes.data);
      setProfile(profileRes.data);
      setAiSettings(aiRes.data);
      
      setBudgetJson(JSON.stringify(budgetRes.data, null, 2));
      setProfileJson(JSON.stringify(profileRes.data, null, 2));
    } catch (error) {
      console.error('Failed to fetch settings', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      let finalBudget = budget;
      let finalProfile = profile;

      if (activeTab === 'json') {
        finalBudget = JSON.parse(budgetJson);
        finalProfile = JSON.parse(profileJson);
      }

      await Promise.all([
        client.put('/api/settings/budget', finalBudget),
        client.put('/api/settings/profile', finalProfile)
      ]);
      
      setBudget(finalBudget);
      setProfile(finalProfile);
      setMessage({ text: '設定を保存しました', type: 'success' });
    } catch (error: any) {
      setMessage({ text: `保存に失敗しました: ${error.message}`, type: 'error' });
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
      setMessage({ text: 'モデルの変更に失敗しました', type: 'error' });
    } finally {
      setSaving(false);
    }
  };

  const updateProfileField = (path: string, value: any) => {
    const newProfile = { ...profile };
    const keys = path.split('.');
    let current = newProfile;
    for (let i = 0; i < keys.length - 1; i++) {
      current = current[keys[i]];
    }
    current[keys[keys.length - 1]] = value;
    setProfile(newProfile);
    setProfileJson(JSON.stringify(newProfile, null, 2));
  };

  const updateBudgetField = (path: string, value: any) => {
    const newBudget = { ...budget };
    const keys = path.split('.');
    let current = newBudget;
    for (let i = 0; i < keys.length - 1; i++) {
      current = current[keys[i]];
    }
    current[keys[keys.length - 1]] = value;
    setBudget(newBudget);
    setBudgetJson(JSON.stringify(newBudget, null, 2));
  };

  if (loading) return <div className="page-content">読み込み中...</div>;

  return (
    <>
      <TopHeader title="設定" onRefresh={fetchSettings} />
      
      <div className="page-content">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <div className="timeframe-tabs">
            <button className={`tab-btn ${activeTab === 'ui' ? 'active' : ''}`} onClick={() => setActiveTab('ui')}>
              <SettingsIcon size={16} className="mr-2" /> かんたん設定
            </button>
            <button className={`tab-btn ${activeTab === 'json' ? 'active' : ''}`} onClick={() => setActiveTab('json')}>
              <Code size={16} className="mr-2" /> 高度な設定 (JSON)
            </button>
          </div>
          <button className="btn-primary" onClick={handleSave} disabled={saving}>
            <Save size={18} className="mr-2" /> すべての設定を保存
          </button>
        </div>

        {message && (
          <div className={`review-summary mb-4 ${message.type === 'error' ? 'border-danger' : ''}`} 
               style={{ borderLeftColor: message.type === 'error' ? 'var(--danger)' : 'var(--success)' }}>
            {message.type === 'error' && <AlertTriangle size={16} className="text-danger inline mr-2" />}
            {message.text}
          </div>
        )}

        {activeTab === 'ui' ? (
          <div className="dashboard-grid" style={{ padding: 0 }}>
            {/* AI Model Selection */}
            <div className="card section-budget" style={{ gridColumn: 'span 12' }}>
              <div className="card-header">
                <h3><Bot size={20} /> AI モデル設定</h3>
              </div>
              <div className="card-body">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                  {aiSettings?.available_models.map((model: AIModel) => (
                    <div 
                      key={model.id} 
                      className={`p-4 border rounded-lg cursor-pointer transition-all ${aiSettings.active_model === model.id ? 'border-primary bg-primary-light' : 'hover:border-gray-400'}`}
                      style={{ 
                        padding: '1rem',
                        borderRadius: '8px',
                        border: '1px solid',
                        borderColor: aiSettings.active_model === model.id ? 'var(--primary)' : 'var(--border)',
                        backgroundColor: aiSettings.active_model === model.id ? 'rgba(59, 130, 246, 0.1)' : 'var(--bg-color)',
                        cursor: 'pointer'
                      }}
                      onClick={() => handleModelChange(model.id)}
                    >
                      <div className="font-bold mb-1" style={{ fontWeight: 'bold' }}>{model.name}</div>
                      <div className="text-xs text-muted" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{model.description}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Profile Section */}
            <div className="card section-budget">
              <div className="card-header">
                <h3><User size={20} /> プロフィール設定</h3>
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
                  <label>投資方針</label>
                  <textarea 
                    className="form-control" style={{ height: '80px' }}
                    value={profile?.user?.investment_policy || ''} 
                    onChange={(e) => updateProfileField('user.investment_policy', e.target.value)} 
                  />
                </div>
              </div>
            </div>

            {/* Goals Section */}
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
                    className="form-control" style={{ height: '100px' }}
                    value={profile?.user?.target?.description || ''} 
                    onChange={(e) => updateProfileField('user.target.description', e.target.value)} 
                  />
                </div>
              </div>
            </div>

            {/* Budget Totals Section */}
            <div className="card section-budget" style={{ gridColumn: 'span 12' }}>
              <div className="card-header">
                <h3><Wallet size={20} /> 月間収支目標</h3>
              </div>
              <div className="card-body">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                  <div className="form-group">
                    <label>月間総収入 (予算)</label>
                    <input 
                      type="number" className="form-control" 
                      value={budget?.monthly?.income || 0} 
                      onChange={(e) => updateBudgetField('monthly.income', parseInt(e.target.value))} 
                    />
                  </div>
                  <div className="form-group">
                    <label>貯蓄目標額</label>
                    <input 
                      type="number" className="form-control" 
                      value={budget?.monthly?.savings_goal || 0} 
                      onChange={(e) => updateBudgetField('monthly.savings_goal', parseInt(e.target.value))} 
                    />
                  </div>
                  <div className="form-group">
                    <label>投資目標額</label>
                    <input 
                      type="number" className="form-control" 
                      value={budget?.monthly?.investment_goal || 0} 
                      onChange={(e) => updateBudgetField('monthly.investment_goal', parseInt(e.target.value))} 
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Category Budget Section (Variable) */}
            <div className="card section-budget" style={{ gridColumn: 'span 12' }}>
              <div className="card-header">
                <h3><SettingsIcon size={20} /> カテゴリ別予算 (変動費)</h3>
              </div>
              <div className="card-body">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }}>
                  {Object.entries(budget?.monthly?.budget?.variable || {}).map(([category, subcategories]: [string, any]) => (
                    <div key={category} style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border)' }}>
                      <div style={{ fontWeight: 'bold', marginBottom: '1rem', color: 'var(--primary)' }}>{category}</div>
                      {Object.entries(subcategories).map(([sub, amount]: [string, any]) => (
                        <div key={sub} className="form-group" style={{ marginBottom: '0.5rem' }}>
                          <label style={{ fontSize: '0.8rem' }}>{sub}</label>
                          <input 
                            type="number" className="form-control" 
                            value={amount} 
                            onChange={(e) => {
                              const newBudget = { ...budget };
                              newBudget.monthly.budget.variable[category][sub] = parseInt(e.target.value);
                              setBudget(newBudget);
                            }} 
                          />
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="dashboard-grid" style={{ padding: 0 }}>
            <div className="card" style={{ gridColumn: 'span 6' }}>
              <div className="card-header"><h3>budget.json</h3></div>
              <textarea 
                className="form-control" 
                style={{ height: '500px', fontFamily: 'monospace', fontSize: '12px' }}
                value={budgetJson}
                onChange={(e) => setBudgetJson(e.target.value)}
              />
            </div>
            <div className="card" style={{ gridColumn: 'span 6' }}>
              <div className="card-header"><h3>profile.json</h3></div>
              <textarea 
                className="form-control" 
                style={{ height: '500px', fontFamily: 'monospace', fontSize: '12px' }}
                value={profileJson}
                onChange={(e) => setProfileJson(e.target.value)}
              />
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default Settings;
