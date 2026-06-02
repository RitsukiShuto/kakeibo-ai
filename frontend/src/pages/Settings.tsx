import React, { useEffect, useState } from 'react';
import { Settings as SettingsIcon, Save, AlertTriangle, Bot, User, Wallet, Code, ArrowRightLeft, Upload, Server } from 'lucide-react';
import client from '../api/client';
import type { AISettings as AISettingsType } from '../api/client';
import TopHeader from '../components/TopHeader';

// Sub-components
import AISettings from '../components/settings/AISettings';
import ProfileSettings from '../components/settings/ProfileSettings';
import BudgetSettings from '../components/settings/BudgetSettings';
import MappingSettings from '../components/settings/MappingSettings';
import ImportSettings from '../components/settings/ImportSettings';
import ServiceSettings from '../components/settings/ServiceSettings';

const Settings: React.FC = () => {
  const [budget, setBudget] = useState<any>(null);
  const [profile, setProfile] = useState<any>(null);
  const [mapping, setMapping] = useState<any>(null);
  const [aiSettings, setAiSettings] = useState<AISettingsType | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [suggesting, setSuggesting] = useState(false);
  const [activeMode, setActiveMode] = useState<'ui' | 'json'>('ui');
  const [activeTab, setActiveTab] = useState<'ai' | 'profile' | 'budget' | 'mapping' | 'import' | 'system'>('budget');
  const [message, setMessage] = useState<{ text: string, type: 'success' | 'error' } | null>(null);
  const [confirmModal, setConfirmModal] = useState<{ isOpen: boolean, modelId: string | null }>({ isOpen: false, modelId: null });
  const [aiSuggestions, setAiSuggestions] = useState<any[]>([]);
  const [hoveredSuggestion, setHoveredSuggestion] = useState<number | null>(null);
  const [envSettings, setEnvSettings] = useState<any>({});
  const [cronSettings, setCronSettings] = useState<any>({ enabled: true, time: '23:50', timeframe: 'weekly' });
  const [importFiles, setImportFiles] = useState<File[]>([]);
  const [importResult, setImportResult] = useState<{ totalFiles: number; totalImported: number; details: any[] } | null>(null);
  const [importing, setImporting] = useState(false);

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
      const [budgetRes, profileRes, aiRes, mappingRes, envRes, cronRes] = await Promise.all([
        client.get('/api/settings/budget'),
        client.get('/api/settings/profile'),
        client.get<AISettingsType>('/api/settings/ai-models'),
        client.get('/api/settings/mapping'),
        client.get('/api/settings/env'),
        client.get('/api/settings/cron')
      ]);
      
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
      setEnvSettings(envRes.data);
      setCronSettings(cronRes.data);
      
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
        client.put('/api/settings/mapping', finalMapping),
        client.put('/api/settings/env', envSettings),
        client.put('/api/settings/cron', cronSettings)
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

  const handleImportCsv = async () => {
    if (importFiles.length === 0) return;
    setImporting(true);
    setImportResult(null);
    const formData = new FormData();
    importFiles.forEach(file => formData.append('files', file));
    try {
      const res = await client.post('/api/import/csv', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      const data = res.data;
      setImportResult({ totalFiles: data.total_files, totalImported: data.total_imported, details: data.details });
      setMessage({ text: `${data.total_files}ファイル中、${data.total_imported}件の取引をインポートしました`, type: 'success' });
      setImportFiles([]);
      const fileInput = document.getElementById('csv-file-input') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
    } catch (error: any) {
      setMessage({ text: `インポートに失敗しました: ${error.message}`, type: 'error' });
    } finally {
      setImporting(false);
    }
  };

  const updateEnvField = (key: string, value: string) => {
    setEnvSettings({ ...envSettings, [key]: value });
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
    const name = window.prompt('新しい項目の名前を入力してください');
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

  if (loading) return <div className="page-content">読み込み中...</div>;

  return (
    <>
      <TopHeader title="システム設定" onRefresh={fetchSettings} />
      
      <div className="page-content" style={{ maxWidth: '1000px', margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <div className="timeframe-tabs glass" style={{ padding: '4px' }}>
            <button className={`tab-btn ${activeMode === 'ui' ? 'active' : ''}`} onClick={() => setActiveMode('ui')}>
              <SettingsIcon size={16} /> かんたん設定
            </button>
            <button className={`tab-btn ${activeMode === 'json' ? 'active' : ''}`} onClick={() => setActiveMode('json')}>
              <Code size={16} /> 高度な設定 (JSON)
            </button>
          </div>
          <button className="btn-primary" onClick={handleSave} disabled={saving} style={{ padding: '8px 20px', borderRadius: '10px' }}>
            <Save size={18} style={{ marginRight: '8px' }} /> 設定を保存
          </button>
        </div>

        {message && (
          <div className={`review-summary mb-6 ${message.type === 'error' ? 'border-danger' : ''}`} 
               style={{ borderLeftColor: message.type === 'error' ? 'var(--danger)' : 'var(--success)' }}>
            {message.type === 'error' && <AlertTriangle size={16} className="text-danger inline mr-2" />}
            {message.text}
          </div>
        )}

        {activeMode === 'ui' && (
          <div className="timeframe-tabs mb-8" style={{ background: 'transparent', border: 'none', padding: 0, gap: '2rem', justifyContent: 'center' }}>
            <button className={`tab-link ${activeTab === 'budget' ? 'active' : ''}`} onClick={() => setActiveTab('budget')}>
              <Wallet size={18} /> 予算
            </button>
            <button className={`tab-link ${activeTab === 'ai' ? 'active' : ''}`} onClick={() => setActiveTab('ai')}>
              <Bot size={18} /> AI人格
            </button>
            <button className={`tab-link ${activeTab === 'profile' ? 'active' : ''}`} onClick={() => setActiveTab('profile')}>
              <User size={18} /> プロフィール
            </button>
            <button className={`tab-link ${activeTab === 'mapping' ? 'active' : ''}`} onClick={() => setActiveTab('mapping')}>
              <ArrowRightLeft size={18} /> 分類変換
            </button>
            <button className={`tab-link ${activeTab === 'import' ? 'active' : ''}`} onClick={() => setActiveTab('import')}>
              <Upload size={18} /> インポート
            </button>
            <button className={`tab-link ${activeTab === 'system' ? 'active' : ''}`} onClick={() => setActiveTab('system')}>
              <Server size={18} /> システム
            </button>
          </div>
        )}

        {activeMode === 'ui' ? (
          <div className="settings-content animate-in">
            {activeTab === 'ai' && (
              <AISettings aiSettings={aiSettings} handleModelChange={handleModelChange} handlePersonaChange={handlePersonaChange} />
            )}
            {activeTab === 'profile' && (
              <ProfileSettings profile={profile} updateProfileField={updateProfileField} />
            )}
            {activeTab === 'budget' && (
              <BudgetSettings 
                budget={budget} updateBudgetField={updateBudgetField} 
                handleAddCategory={handleAddCategory} handleDeleteCategory={handleDeleteCategory} 
                setBudget={setBudget} setBudgetJson={setBudgetJson}
              />
            )}
            {activeTab === 'mapping' && (
              <MappingSettings 
                mapping={mapping} handleSuggestMappings={handleSuggestMappings} suggesting={suggesting} 
                aiSuggestions={aiSuggestions} applySuggestion={applySuggestion} 
                hoveredSuggestion={hoveredSuggestion} setHoveredSuggestion={setHoveredSuggestion}
                setMapping={setMapping} setMappingJson={setMappingJson}
              />
            )}
            {activeTab === 'import' && (
              <ImportSettings 
                importFiles={importFiles} setImportFiles={setImportFiles} 
                handleImportCsv={handleImportCsv} importing={importing} importResult={importResult} 
              />
            )}
            {activeTab === 'system' && (
              <ServiceSettings 
                envSettings={envSettings} updateEnvField={updateEnvField} 
                cronSettings={cronSettings} setCronSettings={setCronSettings} 
              />
            )}
          </div>
        ) : (
          <div className="dashboard-grid" style={{ padding: 0 }}>
            <div className="card" style={{ gridColumn: 'span 4' }}>
              <div className="card-header"><h3>budget.json</h3></div>
              <textarea 
                className="form-control" 
                style={{ height: '500px', fontFamily: 'monospace', fontSize: '13px', background: 'rgba(0,0,0,0.2)' }}
                value={budgetJson}
                onChange={(e) => setBudgetJson(e.target.value)}
              />
            </div>
            <div className="card" style={{ gridColumn: 'span 4' }}>
              <div className="card-header"><h3>profile.json</h3></div>
              <textarea 
                className="form-control" 
                style={{ height: '500px', fontFamily: 'monospace', fontSize: '13px', background: 'rgba(0,0,0,0.2)' }}
                value={profileJson}
                onChange={(e) => setProfileJson(e.target.value)}
              />
            </div>
            <div className="card" style={{ gridColumn: 'span 4' }}>
              <div className="card-header"><h3>mapping.json</h3></div>
              <textarea 
                className="form-control" 
                style={{ height: '500px', fontFamily: 'monospace', fontSize: '13px', background: 'rgba(0,0,0,0.2)' }}
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
      `}</style>
    </>
  );
};

export default Settings;
