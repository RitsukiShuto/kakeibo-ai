import React, { useEffect, useState } from 'react';
import { Settings as SettingsIcon, Save, AlertTriangle, Bot, User, Target, Wallet, Code, CheckCircle2, ArrowRightLeft, Plus, Trash2, TrendingUp, Database, RefreshCcw } from 'lucide-react';
import client from '../api/client';
import type { AISettings } from '../api/client';
import TopHeader from '../components/TopHeader';

const Settings: React.FC = () => {
  const [budget, setBudget] = useState<any>(null);
  const [profile, setProfile] = useState<any>(null);
  const [mapping, setMapping] = useState<any>(null);
  const [aiSettings, setAiSettings] = useState<AISettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [suggesting, setSuggesting] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [activeMode, setActiveMode] = useState<'ui' | 'json'>('ui');
  const [activeTab, setActiveTab] = useState<'ai' | 'profile' | 'budget' | 'mapping' | 'lifeplan' | 'data'>('ai');
  const [message, setMessage] = useState<{ text: string, type: 'success' | 'error' } | null>(null);
  const [confirmModal, setConfirmModal] = useState<{ isOpen: boolean, modelId: string | null }>({ isOpen: false, modelId: null });
  const [aiSuggestions, setAiSuggestions] = useState<any[]>([]);
  const [hoveredSuggestion, setHoveredSuggestion] = useState<number | null>(null);

  // JSON string states for the 'Advanced' tab
  const [budgetJson, setBudgetJson] = useState('');
  const [profileJson, setProfileJson] = useState('');
  const [mappingJson, setMappingJson] = useState('');

  // Load suggestions from sessionStorage on mount
  useEffect(() => {
    const saved = sessionStorage.getItem('ai_mapping_suggestions');
    if (saved) {
      try {
        setAiSuggestions(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to parse saved suggestions', e);
      }
    }
  }, []);

  // Save suggestions to sessionStorage when they change
  useEffect(() => {
    sessionStorage.setItem('ai_mapping_suggestions', JSON.stringify(aiSuggestions));
  }, [aiSuggestions]);

  const fetchSettings = async () => {
    setLoading(true);
    try {
      const [budgetRes, profileRes, aiRes, mappingRes] = await Promise.all([
        client.get('/api/settings/budget'),
        client.get('/api/settings/profile'),
        client.get<AISettings>('/api/settings/ai-models'),
        client.get('/api/settings/mapping')
      ]);
      
      // 旧形式の budget.json を正規化: monthly.categories → monthly.budget.variable
      let budgetData = budgetRes.data;
      if (budgetData?.monthly && !budgetData.monthly.budget) {
        const oldCategories = budgetData.monthly.categories || {};
        budgetData = {
          ...budgetData,
          monthly: {
            ...budgetData.monthly,
            budget: {
              fixed: {},
              variable: Object.fromEntries(
                Object.entries(oldCategories).map(([cat, amt]) => [cat, amt])
              )
            }
          }
        };
      }
      
      setBudget(budgetData);
      setProfile(profileRes.data);
      setAiSettings(aiRes.data);
      setMapping(mappingRes.data);
      
      setBudgetJson(JSON.stringify(budgetData, null, 2));
      setProfileJson(JSON.stringify(profileRes.data, null, 2));
      setMappingJson(JSON.stringify(mappingRes.data, null, 2));
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
      let finalMapping = mapping;

      if (activeMode === 'json') {
        finalBudget = JSON.parse(budgetJson);
        finalProfile = JSON.parse(profileJson);
        finalMapping = JSON.parse(mappingJson);
      }

      await Promise.all([
        client.put('/api/settings/budget', finalBudget),
        client.put('/api/settings/profile', finalProfile),
        client.put('/api/settings/mapping', finalMapping)
      ]);
      
      setBudget(finalBudget);
      setProfile(finalProfile);
      setMapping(finalMapping);
      setMessage({ text: '設定を保存しました', type: 'success' });
      setTimeout(() => setMessage(null), 3000);
    } catch (error: any) {
      setMessage({ text: `保存に失敗しました: ${error.message}`, type: 'error' });
      setTimeout(() => setMessage(null), 5000);
    } finally {
      setSaving(false);
    }
  };

  const handleSuggestMappings = async () => {
    setSuggesting(true);
    try {
      const res = await client.post('/api/settings/mapping/suggest');
      setAiSuggestions(res.data);
      if (res.data.length === 0) {
        setMessage({ text: '新しいマッピングの提案はありません', type: 'success' });
      }
    } catch (error) {
      setMessage({ text: '提案の取得に失敗しました', type: 'error' });
    } finally {
      setSuggesting(false);
    }
  };

  const applySuggestion = (s: any) => {
    const newMapping = { ...mapping };
    if (s.suggested_category && s.suggested_category !== s.raw_category) {
      if (!newMapping.category_mappings) newMapping.category_mappings = {};
      newMapping.category_mappings[s.raw_category] = s.suggested_category;
    }
    
    if (s.suggested_genre && s.suggested_genre !== s.raw_genre) {
      if (!newMapping.genre_mappings) newMapping.genre_mappings = {};
      if (s.suggested_category) {
        newMapping.genre_mappings[s.raw_genre] = { category: s.suggested_category, genre: s.suggested_genre };
      } else {
        newMapping.genre_mappings[s.raw_genre] = s.suggested_genre;
      }
    }
    
    setMapping(newMapping);
    setMappingJson(JSON.stringify(newMapping, null, 2));
    setAiSuggestions(prev => prev.filter(item => item !== s));
  };

  const handleModelChange = (modelId: string) => {
    if (aiSettings?.active_model === modelId) return;
    setConfirmModal({ isOpen: true, modelId });
  };

  const confirmModelChange = async () => {
    const modelId = confirmModal.modelId;
    if (!modelId) return;
    
    setConfirmModal({ isOpen: false, modelId: null });
    setSaving(true);
    try {
      await client.put('/api/settings/active-model', { active_model: modelId });
      setAiSettings(prev => prev ? { ...prev, active_model: modelId } : null);
      setMessage({ text: 'AIモデルを変更しました', type: 'success' });
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      setMessage({ text: 'モデルの変更に失敗しました', type: 'error' });
      setTimeout(() => setMessage(null), 5000);
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

  const handleAddCategory = (section: string) => {
    const name = window.prompt('新しい項目の名前（例: 食費、通信費）を入力してください');
    if (!name || name.trim() === '') return;
    
    const newBudget = { ...budget };
    if (!newBudget.monthly.budget) newBudget.monthly.budget = { fixed: {}, variable: {} };
    if (!newBudget.monthly.budget[section]) newBudget.monthly.budget[section] = {};
    
    if (newBudget.monthly.budget[section][name] !== undefined) {
      alert('その項目は既に存在します');
      return;
    }
    
    newBudget.monthly.budget[section][name] = 0;
    setBudget(newBudget);
    setBudgetJson(JSON.stringify(newBudget, null, 2));
  };

  const handleDeleteCategory = (section: string, category: string) => {
    if (window.confirm(`「${category}」を削除してもよろしいですか？`)) {
      const newBudget = { ...budget };
      delete newBudget.monthly.budget[section][category];
      setBudget(newBudget);
      setBudgetJson(JSON.stringify(newBudget, null, 2));
    }
  };

  const handleDataSync = async () => {
    setSyncing(true);
    setMessage(null);
    try {
      await client.post('/api/fetch');
      setMessage({ text: 'データの同期を開始しました。完了まで数分かかる場合があります。数分後に画面を更新してください。', type: 'success' });
    } catch (error) {
      console.error('Failed to start data sync', error);
      setMessage({ text: 'データの同期開始に失敗しました。', type: 'error' });
    } finally {
      setSyncing(false);
    }
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
            <button className={`tab-link ${activeTab === 'mapping' ? 'active' : ''}`} onClick={() => setActiveTab('mapping')}>
              <ArrowRightLeft size={18} /> カテゴリ変換
            </button>
            <button className={`tab-link ${activeTab === 'lifeplan' ? 'active' : ''}`} onClick={() => setActiveTab('lifeplan')}>
              <TrendingUp size={18} /> ライフプラン設定
            </button>
            <button className={`tab-link ${activeTab === 'data' ? 'active' : ''}`} onClick={() => setActiveTab('data')}>
              <Database size={18} /> データ管理
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
                      {aiSettings?.available_models?.map((model) => (
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
                        {(() => {
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
                          
                          return renderPolicyEditor(profile?.user?.investment_policy || {});
                        })()}
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
            )}

            {activeTab === 'budget' && (() => {
              const incomeAmount = budget?.monthly?.income || 0;
              let totalBudgetAmount = 0;
              totalBudgetAmount += budget?.monthly?.savings_goal || 0;
              totalBudgetAmount += budget?.monthly?.investment_goal || 0;
              
              const calcSection = (sectionData: any) => {
                if (!sectionData) return;
                Object.values(sectionData).forEach((val: any) => {
                  if (typeof val === 'number') totalBudgetAmount += val;
                  else if (typeof val === 'object' && val !== null) {
                    Object.values(val).forEach((v: any) => {
                      if (typeof v === 'number') totalBudgetAmount += v;
                    });
                  }
                });
              };
              calcSection(budget?.monthly?.budget?.fixed);
              calcSection(budget?.monthly?.budget?.variable);
              
              const isOverBudget = incomeAmount > 0 && totalBudgetAmount > incomeAmount;

              const surplus = incomeAmount - totalBudgetAmount;

              return (
                <div className="flex flex-col gap-6" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                  {isOverBudget && (
                    <div className="review-summary" style={{ borderLeftColor: 'var(--danger)', backgroundColor: 'rgba(239, 68, 68, 0.1)', color: 'var(--text-main)' }}>
                      <AlertTriangle size={18} className="text-danger inline mr-2" style={{ verticalAlign: 'text-bottom' }} />
                      <span className="font-bold">警告: </span>
                      予算・目標の合計（{totalBudgetAmount.toLocaleString()}円）が、月間総収入（{incomeAmount.toLocaleString()}円）を上回っています。このままでは赤字になる可能性があります。
                    </div>
                  )}

                <div className="card">
                  <div className="card-header">
                    <h3><Wallet size={20} /> 全体目標</h3>
                  </div>
                  <div className="card-body">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
                      <div className="form-group mb-0">
                        <label>月間総収入</label>
                        <input 
                          type="number" className="form-control" 
                          value={budget?.monthly?.income || 0} 
                          onChange={(e) => updateBudgetField('monthly.income', parseInt(e.target.value))} 
                        />
                      </div>
                      <div className="form-group mb-0">
                        <label>貯蓄目標額</label>
                        <input 
                          type="number" className="form-control" 
                          value={budget?.monthly?.savings_goal || 0} 
                          onChange={(e) => updateBudgetField('monthly.savings_goal', parseInt(e.target.value))} 
                        />
                      </div>
                      <div className="form-group mb-0">
                        <label>投資目標額</label>
                        <input 
                          type="number" className="form-control" 
                          value={budget?.monthly?.investment_goal || 0} 
                          onChange={(e) => updateBudgetField('monthly.investment_goal', parseInt(e.target.value))} 
                        />
                      </div>
                      <div className="form-group mb-0" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '8px', border: `1px solid ${surplus >= 0 ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}` }}>
                        <label style={{ color: surplus >= 0 ? 'var(--success)' : 'var(--danger)' }}>割り振り可能な余剰資金</label>
                        <div style={{ fontSize: '1.4rem', fontWeight: 'bold', color: surplus >= 0 ? 'var(--success)' : 'var(--danger)', marginTop: 'auto' }}>
                          {surplus >= 0 ? '+' : ''}{surplus.toLocaleString()} 円
                        </div>
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
                          <div key={category} className="budget-category-box" style={{ position: 'relative' }}>
                            <button 
                              onClick={() => handleDeleteCategory(section, category)}
                              style={{ position: 'absolute', top: '16px', right: '16px', background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '1.2rem', lineHeight: 1 }}
                              title="この項目を削除"
                            >×</button>
                            <div className="budget-category-title" style={{ paddingRight: '24px' }}>{category}</div>
                            {typeof subcategories === 'object' ? (
                              Object.entries(subcategories).map(([sub, amount]: [string, any]) => (
                                <div key={sub} className="form-group mb-2">
                                  <label style={{ fontSize: '0.75rem' }}>{sub}</label>
                                  <input 
                                    type="number" className="form-control form-control-sm" 
                                    value={amount} 
                                    onChange={(e) => {
                                      const newBudget = { ...budget };
                                      newBudget.monthly.budget[section][category][sub] = parseInt(e.target.value) || 0;
                                      setBudget(newBudget);
                                      setBudgetJson(JSON.stringify(newBudget, null, 2));
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
                                    newBudget.monthly.budget[section][category] = parseInt(e.target.value) || 0;
                                    setBudget(newBudget);
                                    setBudgetJson(JSON.stringify(newBudget, null, 2));
                                  }} 
                                />
                              </div>
                            )}
                          </div>
                        ))}
                        
                        <div 
                          className="budget-category-box" 
                          style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', borderStyle: 'dashed', cursor: 'pointer', background: 'transparent', opacity: 0.7, minHeight: '120px' }}
                          onClick={() => handleAddCategory(section)}
                        >
                          <span style={{ color: 'var(--primary)', fontWeight: 'bold', fontSize: '1.1rem' }}>+ 新規項目を追加</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              );
            })()}

            {activeTab === 'mapping' && (
              <div className="flex flex-col gap-6" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <div className="card" style={{ border: '1px solid var(--primary)', background: 'rgba(59, 130, 246, 0.05)' }}>
                  <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h3 style={{ color: 'var(--primary)' }}><Bot size={20} /> AI マッピング提案</h3>
                    <button 
                      className="btn-primary" 
                      onClick={handleSuggestMappings} 
                      disabled={suggesting}
                      style={{ padding: '4px 12px', fontSize: '0.85rem' }}
                    >
                      {suggesting ? '考え中...' : 'AIにマッピングを相談する'}
                    </button>
                  </div>
                  <div className="card-body">
                    <p className="text-muted mb-4" style={{ fontSize: '0.85rem' }}>
                      DB内の未分類項目をスキャンし、予算設定に基づいた最適なマッピングをAIが提案します。
                    </p>
                    {aiSuggestions.length > 0 ? (
                      <div className="flex flex-col gap-3">
                        {aiSuggestions.map((s, idx) => (
                          <div 
                            key={idx} 
                            className="suggestion-item" 
                            style={{ position: 'relative', background: 'var(--bg-color)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                            onMouseEnter={() => setHoveredSuggestion(idx)}
                            onMouseLeave={() => setHoveredSuggestion(null)}
                          >
                            <div style={{ flex: 1 }}>
                              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                {s.raw_category} {s.raw_genre ? `> ${s.raw_genre}` : ''}
                              </div>
                              <div style={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <ArrowRightLeft size={14} className="text-primary" />
                                {s.suggested_category} {s.suggested_genre ? `> ${s.suggested_genre}` : ''}
                              </div>
                              <div style={{ fontSize: '0.7rem', color: 'var(--success)', marginTop: '4px' }}>
                                理由: {s.reason}
                              </div>
                            </div>
                            <button className="btn-outline" onClick={() => applySuggestion(s)} style={{ padding: '4px 8px', fontSize: '0.75rem' }}>
                              採用
                            </button>

                            {hoveredSuggestion === idx && s.examples && s.examples.length > 0 && (
                              <div className="card glass" style={{ 
                                position: 'absolute', top: '100%', left: 0, right: 0, zIndex: 100, 
                                marginTop: '4px', padding: '12px', fontSize: '0.75rem', 
                                background: 'var(--card-bg)', border: '1px solid var(--primary)' 
                              }}>
                                <div style={{ fontWeight: 'bold', marginBottom: '8px', color: 'var(--primary)' }}>該当する直近の明細:</div>
                                {s.examples.map((ex: any, eidx: number) => (
                                  <div key={eidx} style={{ display: 'flex', gap: '8px', marginBottom: '4px' }}>
                                    <span style={{ color: 'var(--text-muted)' }}>{ex.transaction_date}</span>
                                    <span style={{ flex: 1 }}>{ex.comment}</span>
                                    <span style={{ fontWeight: 'bold' }}>{ex.amount.toLocaleString()}円</span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : !suggesting && (
                      <div className="text-center py-4 text-muted" style={{ fontSize: '0.85rem' }}>
                        「相談する」ボタンを押すと、新しい提案が表示されます。
                      </div>
                    )}
                  </div>
                </div>

                <div className="card">
                  <div className="card-header">
                    <h3><ArrowRightLeft size={20} /> 大項目の変換ルール (Category Mapping)</h3>
                  </div>
                  <div className="card-body">
                    <p className="text-muted mb-4" style={{ fontSize: '0.85rem' }}>
                      MoneyForwardやZaimの「大項目」を、独自のカテゴリ名に変換します。
                    </p>
                    <table className="table">
                      <thead>
                        <tr>
                          <th>元のカテゴリ名 (Raw)</th>
                          <th style={{ width: '40px' }}></th>
                          <th>変換後のカテゴリ名 (Mapped)</th>
                          <th style={{ width: '60px' }}></th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(mapping?.category_mappings || {}).map(([raw, mapped]) => (
                          <tr key={raw}>
                            <td>{raw}</td>
                            <td style={{ textAlign: 'center' }}>→</td>
                            <td>
                              <input 
                                type="text" className="form-control form-control-sm" 
                                value={mapped as string} 
                                onChange={(e) => {
                                  const newMapping = { ...mapping };
                                  newMapping.category_mappings[raw] = e.target.value;
                                  setMapping(newMapping);
                                  setMappingJson(JSON.stringify(newMapping, null, 2));
                                }}
                              />
                            </td>
                            <td style={{ textAlign: 'center' }}>
                              <button 
                                className="btn-icon text-danger" 
                                onClick={() => {
                                  const newMapping = { ...mapping };
                                  delete newMapping.category_mappings[raw];
                                  setMapping(newMapping);
                                  setMappingJson(JSON.stringify(newMapping, null, 2));
                                }}
                              >
                                <Trash2 size={16} />
                              </button>
                            </td>
                          </tr>
                        ))}
                        <tr>
                          <td>
                            <input type="text" id="new-cat-raw" className="form-control form-control-sm" placeholder="未分類" />
                          </td>
                          <td style={{ textAlign: 'center' }}>→</td>
                          <td>
                            <input type="text" id="new-cat-mapped" className="form-control form-control-sm" placeholder="その他" />
                          </td>
                          <td style={{ textAlign: 'center' }}>
                            <button 
                              className="btn-icon text-primary"
                              onClick={() => {
                                const raw = (document.getElementById('new-cat-raw') as HTMLInputElement).value;
                                const mapped = (document.getElementById('new-cat-mapped') as HTMLInputElement).value;
                                if (raw && mapped) {
                                  const newMapping = { ...mapping };
                                  if (!newMapping.category_mappings) newMapping.category_mappings = {};
                                  newMapping.category_mappings[raw] = mapped;
                                  setMapping(newMapping);
                                  setMappingJson(JSON.stringify(newMapping, null, 2));
                                  (document.getElementById('new-cat-raw') as HTMLInputElement).value = '';
                                  (document.getElementById('new-cat-mapped') as HTMLInputElement).value = '';
                                }
                              }}
                            >
                              <Plus size={18} />
                            </button>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <div className="card">
                  <div className="card-header">
                    <h3><ArrowRightLeft size={20} /> 中項目の変換・上書きルール (Genre Mapping)</h3>
                  </div>
                  <div className="card-body">
                    <p className="text-muted mb-4" style={{ fontSize: '0.85rem' }}>
                      「中項目」の名前に基づいて、中項目名のみ、または大項目も含めて変換します。<br/>
                      例: 「コンビニ」という中項目を「日用品」という中項目に変更する、など。
                    </p>
                    <table className="table">
                      <thead>
                        <tr>
                          <th>元の中項目名 (Raw)</th>
                          <th style={{ width: '40px' }}></th>
                          <th>変換後のカテゴリ/中項目</th>
                          <th style={{ width: '60px' }}></th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(mapping?.genre_mappings || {}).map(([raw, rule]: [string, any]) => (
                          <tr key={raw}>
                            <td>{raw}</td>
                            <td style={{ textAlign: 'center' }}>→</td>
                            <td>
                              <div style={{ display: 'flex', gap: '8px' }}>
                                <div style={{ flex: 1 }}>
                                  <label style={{ fontSize: '0.7rem' }}>大項目(任意)</label>
                                  <input 
                                    type="text" className="form-control form-control-sm" 
                                    placeholder="大項目"
                                    value={typeof rule === 'object' ? rule.category : ''} 
                                    onChange={(e) => {
                                      const newMapping = { ...mapping };
                                      if (typeof rule !== 'object') {
                                        newMapping.genre_mappings[raw] = { category: e.target.value, genre: rule };
                                      } else {
                                        newMapping.genre_mappings[raw].category = e.target.value;
                                      }
                                      setMapping(newMapping);
                                      setMappingJson(JSON.stringify(newMapping, null, 2));
                                    }}
                                  />
                                </div>
                                <div style={{ flex: 1 }}>
                                  <label style={{ fontSize: '0.7rem' }}>中項目</label>
                                  <input 
                                    type="text" className="form-control form-control-sm" 
                                    placeholder="中項目"
                                    value={typeof rule === 'object' ? rule.genre : rule} 
                                    onChange={(e) => {
                                      const newMapping = { ...mapping };
                                      if (typeof rule !== 'object') {
                                        newMapping.genre_mappings[raw] = e.target.value;
                                      } else {
                                        newMapping.genre_mappings[raw].genre = e.target.value;
                                      }
                                      setMapping(newMapping);
                                      setMappingJson(JSON.stringify(newMapping, null, 2));
                                    }}
                                  />
                                </div>
                              </div>
                            </td>
                            <td style={{ textAlign: 'center', verticalAlign: 'bottom' }}>
                              <button 
                                className="btn-icon text-danger" 
                                onClick={() => {
                                  const newMapping = { ...mapping };
                                  delete newMapping.genre_mappings[raw];
                                  setMapping(newMapping);
                                  setMappingJson(JSON.stringify(newMapping, null, 2));
                                }}
                              >
                                <Trash2 size={16} />
                              </button>
                            </td>
                          </tr>
                        ))}
                        <tr>
                          <td>
                            <input type="text" id="new-gen-raw" className="form-control form-control-sm" placeholder="ランチ" />
                          </td>
                          <td style={{ textAlign: 'center' }}>→</td>
                          <td>
                            <div style={{ display: 'flex', gap: '8px' }}>
                              <input type="text" id="new-gen-cat" className="form-control form-control-sm" placeholder="食費(任意)" />
                              <input type="text" id="new-gen-gen" className="form-control form-control-sm" placeholder="昼食" />
                            </div>
                          </td>
                          <td style={{ textAlign: 'center' }}>
                            <button 
                              className="btn-icon text-primary"
                              onClick={() => {
                                const raw = (document.getElementById('new-gen-raw') as HTMLInputElement).value;
                                const cat = (document.getElementById('new-gen-cat') as HTMLInputElement).value;
                                const gen = (document.getElementById('new-gen-gen') as HTMLInputElement).value;
                                if (raw && gen) {
                                  const newMapping = { ...mapping };
                                  if (!newMapping.genre_mappings) newMapping.genre_mappings = {};
                                  if (cat) {
                                    newMapping.genre_mappings[raw] = { category: cat, genre: gen };
                                  } else {
                                    newMapping.genre_mappings[raw] = gen;
                                  }
                                  setMapping(newMapping);
                                  setMappingJson(JSON.stringify(newMapping, null, 2));
                                  (document.getElementById('new-gen-raw') as HTMLInputElement).value = '';
                                  (document.getElementById('new-gen-cat') as HTMLInputElement).value = '';
                                  (document.getElementById('new-gen-gen') as HTMLInputElement).value = '';
                                }
                              }}
                            >
                              <Plus size={18} />
                            </button>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'lifeplan' && (
              <div className="flex flex-col gap-6" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <div className="card">
                  <div className="card-header">
                    <h3><TrendingUp size={20} /> 基本シミュレーション設定</h3>
                  </div>
                  <div className="card-body">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem' }}>
                      <div className="form-group">
                        <label>現在の年齢</label>
                        <input 
                          type="number" className="form-control" 
                          value={profile?.user?.life_plan?.current_age || 30} 
                          onChange={(e) => updateProfileField('user.life_plan.current_age', parseInt(e.target.value))} 
                        />
                      </div>
                      <div className="form-group">
                        <label>引退予定年齢</label>
                        <input 
                          type="number" className="form-control" 
                          value={profile?.user?.life_plan?.retirement_age || 65} 
                          onChange={(e) => updateProfileField('user.life_plan.retirement_age', parseInt(e.target.value))} 
                        />
                      </div>
                      <div className="form-group">
                        <label>想定運用利回り (%)</label>
                        <input 
                          type="number" step="0.1" className="form-control" 
                          value={profile?.user?.life_plan?.annual_return_rate || 3.0} 
                          onChange={(e) => updateProfileField('user.life_plan.annual_return_rate', parseFloat(e.target.value))} 
                        />
                      </div>
                      <div className="form-group">
                        <label>想定インフレ率 (%)</label>
                        <input 
                          type="number" step="0.1" className="form-control" 
                          value={profile?.user?.life_plan?.annual_inflation_rate || 1.0} 
                          onChange={(e) => updateProfileField('user.life_plan.annual_inflation_rate', parseFloat(e.target.value))} 
                        />
                      </div>
                      <div className="form-group" style={{ gridColumn: 'span 2' }}>
                        <label>引退後の希望月間生活費 (円)</label>
                        <input 
                          type="number" className="form-control" 
                          value={profile?.user?.life_plan?.monthly_living_expenses_post_retirement || 200000} 
                          onChange={(e) => updateProfileField('user.life_plan.monthly_living_expenses_post_retirement', parseInt(e.target.value))} 
                        />
                        <p className="text-xs text-muted mt-1">※この金額はインフレ率に応じて将来的にスライド計算されます。</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="card">
                  <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h3><Wallet size={20} /> ライフイベント（大型支出）</h3>
                    <button 
                      className="btn-outline" 
                      style={{ padding: '4px 12px', fontSize: '0.85rem' }}
                      onClick={() => {
                        const name = window.prompt('イベント名（例: 住宅購入、世界一周）');
                        const age = window.prompt('発生時の年齢（半角数字）');
                        const amount = window.prompt('予定支出額（半角数字）');
                        if (name && age && amount) {
                          const newEvents = [...(profile?.user?.life_plan?.events || []), { name, age: parseInt(age), amount: parseInt(amount) }];
                          updateProfileField('user.life_plan.events', newEvents);
                        }
                      }}
                    >
                      <Plus size={16} style={{ marginRight: '4px' }} /> イベント追加
                    </button>
                  </div>
                  <div className="card-body">
                    <table className="table">
                      <thead>
                        <tr>
                          <th>年齢</th>
                          <th>イベント名</th>
                          <th>支出額</th>
                          <th style={{ width: '50px' }}></th>
                        </tr>
                      </thead>
                      <tbody>
                        {(profile?.user?.life_plan?.events || []).map((event: any, idx: number) => (
                          <tr key={idx}>
                            <td>{event.age}歳</td>
                            <td>{event.name}</td>
                            <td className="text-danger">-{event.amount.toLocaleString()}円</td>
                            <td>
                              <button 
                                className="btn-icon text-danger"
                                onClick={() => {
                                  const newEvents = profile.user.life_plan.events.filter((_: any, i: number) => i !== idx);
                                  updateProfileField('user.life_plan.events', newEvents);
                                }}
                              >
                                <Trash2 size={16} />
                              </button>
                            </td>
                          </tr>
                        ))}
                        {(!profile?.user?.life_plan?.events || profile.user.life_plan.events.length === 0) && (
                          <tr>
                            <td colSpan={4} className="text-center py-4 text-muted">設定されたイベントはありません</td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'data' && (
              <div className="card">
                <div className="card-header">
                  <h3><Database size={20} /> データ管理</h3>
                </div>
                <div className="card-body">
                  <div className="flex flex-col gap-4" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <p className="text-muted">
                      外部サービス（マネーフォワード等）から最新の明細データを取得し、データベースを更新します。<br/>
                      この処理はバックグラウンドで実行されます。
                    </p>
                    <div>
                      <button 
                        className="btn-primary" 
                        onClick={handleDataSync} 
                        disabled={syncing}
                        style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
                      >
                        <RefreshCcw 
                          size={18} 
                          style={{ 
                            animation: syncing ? 'spin 1s linear infinite' : 'none' 
                          }} 
                        />
                        {syncing ? '同期中...' : '最新データを同期'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="dashboard-grid" style={{ padding: 0 }}>
            <div className="card" style={{ gridColumn: 'span 4' }}>
              <div className="card-header"><h3>budget.json</h3></div>
              <textarea 
                className="form-control" 
                style={{ height: '500px', fontFamily: 'monospace', fontSize: '12px' }}
                value={budgetJson}
                onChange={(e) => setBudgetJson(e.target.value)}
              />
            </div>
            <div className="card" style={{ gridColumn: 'span 4' }}>
              <div className="card-header"><h3>profile.json</h3></div>
              <textarea 
                className="form-control" 
                style={{ height: '500px', fontFamily: 'monospace', fontSize: '12px' }}
                value={profileJson}
                onChange={(e) => setProfileJson(e.target.value)}
              />
            </div>
            <div className="card" style={{ gridColumn: 'span 4' }}>
              <div className="card-header"><h3>mapping.json</h3></div>
              <textarea 
                className="form-control" 
                style={{ height: '500px', fontFamily: 'monospace', fontSize: '12px' }}
                value={mappingJson}
                onChange={(e) => setMappingJson(e.target.value)}
              />
            </div>
          </div>
        )}
      </div>

      {confirmModal.isOpen && (
        <div className="modal-overlay" style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, backdropFilter: 'blur(4px)' }}>
          <div className="card glass" style={{ maxWidth: '400px', width: '90%', padding: '24px' }}>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertTriangle className="text-warning" size={24} />
              モデル変更の確認
            </h3>
            <p style={{ color: 'var(--text-muted)', marginBottom: '24px', lineHeight: 1.5 }}>
              AIモデルを「<strong style={{ color: 'var(--text-main)' }}>{confirmModal.modelId}</strong>」に変更しますか？<br/>
              本番環境での分析コストやレスポンス品質に影響する可能性があります。
            </p>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
              <button className="btn-outline" onClick={() => setConfirmModal({ isOpen: false, modelId: null })}>
                キャンセル
              </button>
              <button className="btn-primary" onClick={confirmModelChange}>
                変更する
              </button>
            </div>
          </div>
        </div>
      )}

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
        @keyframes spin {
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </>
  );
};

export default Settings;
