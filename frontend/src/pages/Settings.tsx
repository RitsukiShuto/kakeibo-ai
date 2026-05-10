import React, { useEffect, useState } from 'react';
import { Settings as SettingsIcon, Save, AlertTriangle, Bot, User, Target, Wallet, Code, CheckCircle2 } from 'lucide-react';
import client from '../api/client';
import type { AISettings } from '../api/client';
import TopHeader from '../components/TopHeader';

const Settings: React.FC = () => {
  const [budget, setBudget] = useState<any>(null);
  const [profile, setProfile] = useState<any>(null);
  const [aiSettings, setAiSettings] = useState<AISettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeMode, setActiveMode] = useState<'ui' | 'json'>('ui');
  const [activeTab, setActiveTab] = useState<'ai' | 'profile' | 'budget'>('ai');
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

      if (activeMode === 'json') {
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

  const handlePersonaChange = async (personaId: string) => {
    setSaving(true);
    try {
      await client.put('/api/settings/active-persona', { active_persona: personaId });
      setAiSettings(prev => prev ? { ...prev, active_persona: personaId } : null);
      setMessage({ text: 'AIキャラクターを変更しました', type: 'success' });
    } catch (error) {
      setMessage({ text: 'キャラクターの変更に失敗しました', type: 'error' });
    } finally {
      setSaving(false);
    }
  };

  const updateProfileField = (path: string, value: any) => {
    const newProfile = { ...profile };
    const keys = path.split('.');
    let current = newProfile;
    for (let i = 0; i < keys.length - 1; i++) {
      if (!current[keys[i]]) current[keys[i]] = {};
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
      if (!current[keys[i]]) current[keys[i]] = {};
      current = current[keys[i]];
    }
    current[keys[keys.length - 1]] = value;
    setBudget(newBudget);
    setBudgetJson(JSON.stringify(newBudget, null, 2));
  };

  const renderInvestmentPolicy = () => {
    const val = profile?.user?.investment_policy;
    if (typeof val === 'object' && val !== null) {
      return JSON.stringify(val);
    }
    return val || '';
  };

  if (loading) return <div className="page-content">読み込み中...</div>;

  return (
    <>
      <TopHeader title="設定" onRefresh={fetchSettings} />
      
      <div className="page-content">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <div className="timeframe-tabs">
            <button className={`tab-btn ${activeMode === 'ui' ? 'active' : ''}`} onClick={() => setActiveMode('ui')}>
              <SettingsIcon size={16} style={{ marginRight: '8px' }} /> かんたん設定
            </button>
            <button className={`tab-btn ${activeMode === 'json' ? 'active' : ''}`} onClick={() => setActiveMode('json')}>
              <Code size={16} style={{ marginRight: '8px' }} /> 高度な設定 (JSON)
            </button>
          </div>
          <button className="btn-primary" onClick={handleSave} disabled={saving}>
            <Save size={18} style={{ marginRight: '8px' }} /> 設定を保存
          </button>
        </div>

        {message && (
          <div className={`review-summary mb-4 ${message.type === 'error' ? 'border-danger' : ''}`} 
               style={{ borderLeftColor: message.type === 'error' ? 'var(--danger)' : 'var(--success)' }}>
            {message.type === 'error' && <AlertTriangle size={16} className="text-danger inline mr-2" />}
            {message.text}
          </div>
        )}

        {activeMode === 'ui' && (
          <div className="timeframe-tabs mb-6" style={{ background: 'transparent', border: 'none', padding: 0, gap: '1.5rem' }}>
            <button className={`tab-link ${activeTab === 'ai' ? 'active' : ''}`} onClick={() => setActiveTab('ai')}>
              <Bot size={18} /> AIモデル
            </button>
            <button className={`tab-link ${activeTab === 'profile' ? 'active' : ''}`} onClick={() => setActiveTab('profile')}>
              <User size={18} /> プロフィール
            </button>
            <button className={`tab-link ${activeTab === 'budget' ? 'active' : ''}`} onClick={() => setActiveTab('budget')}>
              <Wallet size={18} /> 予算設定
            </button>
          </div>
        )}

        {activeMode === 'ui' ? (
          <div className="settings-content">
            {activeTab === 'ai' && (
              <div className="flex flex-col gap-6" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <div className="card">
                  <div className="card-header">
                    <h3><Bot size={20} /> AI モデルの選択</h3>
                  </div>
                  <div className="card-body">
                    <div className="model-grid">
                      {aiSettings?.available_models.map((model) => (
                        <div 
                          key={model.id} 
                          className={`model-card ${aiSettings.active_model === model.id ? 'active' : ''}`}
                          onClick={() => handleModelChange(model.id)}
                        >
                          <div className="model-header">
                            <div className="model-name">{model.name}</div>
                            {aiSettings.active_model === model.id && <CheckCircle2 size={18} className="text-primary" />}
                          </div>
                          <div className="model-desc">{model.description}</div>
                          <div className="model-id">{model.id}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="card">
                  <div className="card-header">
                    <h3><User size={20} /> AI キャラクター（人格）の選択</h3>
                  </div>
                  <div className="card-body">
                    <div className="model-grid">
                      {aiSettings?.available_personas?.map((persona) => (
                        <div 
                          key={persona.id} 
                          className={`model-card ${aiSettings.active_persona === persona.id ? 'active' : ''}`}
                          onClick={() => handlePersonaChange(persona.id)}
                          style={{ borderColor: aiSettings.active_persona === persona.id ? 'var(--success)' : '' }}
                        >
                          <div className="model-header">
                            <div className="model-name" style={{ color: aiSettings.active_persona === persona.id ? 'var(--success)' : '' }}>
                              {persona.name}
                            </div>
                            {aiSettings.active_persona === persona.id && <CheckCircle2 size={18} className="text-success" />}
                          </div>
                          <div className="model-desc">{persona.description}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'profile' && (
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
                      <label>投資方針</label>
                      <textarea 
                        className="form-control" style={{ height: '100px' }}
                        value={renderInvestmentPolicy()} 
                        onChange={(e) => updateProfileField('user.investment_policy', e.target.value)} 
                      />
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
            )}

            {activeTab === 'budget' && (
              <div className="flex flex-col gap-6" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <div className="card">
                  <div className="card-header">
                    <h3><Wallet size={20} /> 全体目標</h3>
                  </div>
                  <div className="card-body">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                      <div className="form-group">
                        <label>月間総収入</label>
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

                {['fixed', 'variable'].map((section) => (
                  <div key={section} className="card">
                    <div className="card-header">
                      <h3><SettingsIcon size={20} /> カテゴリ別予算 ({section === 'fixed' ? '固定費' : '変動費'})</h3>
                    </div>
                    <div className="card-body">
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }}>
                        {Object.entries(budget?.monthly?.budget?.[section] || {}).map(([category, subcategories]: [string, any]) => (
                          <div key={category} className="budget-category-box">
                            <div className="budget-category-title">{category}</div>
                            {typeof subcategories === 'object' ? (
                              Object.entries(subcategories).map(([sub, amount]: [string, any]) => (
                                <div key={sub} className="form-group mb-2">
                                  <label style={{ fontSize: '0.75rem' }}>{sub}</label>
                                  <input 
                                    type="number" className="form-control form-control-sm" 
                                    value={amount} 
                                    onChange={(e) => {
                                      const newBudget = { ...budget };
                                      newBudget.monthly.budget[section][category][sub] = parseInt(e.target.value);
                                      setBudget(newBudget);
                                    }} 
                                  />
                                </div>
                              ))
                            ) : (
                              <div className="form-group">
                                <input 
                                  type="number" className="form-control form-control-sm" 
                                  value={subcategories} 
                                  onChange={(e) => {
                                    const newBudget = { ...budget };
                                    newBudget.monthly.budget[section][category] = parseInt(e.target.value);
                                    setBudget(newBudget);
                                  }} 
                                />
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
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

      <style>{`
        .tab-link {
          background: none;
          border: none;
          color: var(--text-muted);
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 8px;
          padding-bottom: 8px;
          border-bottom: 2px solid transparent;
          transition: all 0.2s;
        }
        .tab-link.active {
          color: var(--primary);
          border-bottom-color: var(--primary);
        }
        .model-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
          gap: 1.5rem;
        }
        .model-card {
          background: var(--bg-color);
          border: 1px solid var(--border);
          border-radius: 12px;
          padding: 1.5rem;
          cursor: pointer;
          transition: all 0.2s;
          position: relative;
        }
        .model-card:hover {
          border-color: var(--primary);
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        .model-card.active {
          border-color: var(--primary);
          background: rgba(59, 130, 246, 0.05);
          box-shadow: 0 0 0 1px var(--primary);
        }
        .model-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 1rem;
        }
        .model-name {
          font-weight: bold;
          font-size: 1.1rem;
          color: var(--text-main);
        }
        .model-desc {
          font-size: 0.85rem;
          color: var(--text-muted);
          line-height: 1.5;
          margin-bottom: 1.5rem;
        }
        .model-id {
          font-family: monospace;
          font-size: 0.7rem;
          color: var(--text-muted);
          opacity: 0.5;
        }
        .budget-category-box {
          background: rgba(255,255,255,0.02);
          padding: 1.25rem;
          border-radius: 10px;
          border: 1px solid var(--border);
        }
        .budget-category-title {
          font-weight: bold;
          margin-bottom: 1rem;
          color: var(--primary);
          border-bottom: 1px solid rgba(59, 130, 246, 0.2);
          padding-bottom: 0.5rem;
        }
      `}</style>
    </>
  );
};

export default Settings;
