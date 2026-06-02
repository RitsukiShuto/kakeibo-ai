import React from 'react';
import { Server, AlertTriangle, Cpu, Bell, Calendar } from 'lucide-react';

interface ServiceSettingsProps {
  envSettings: any;
  updateEnvField: (key: string, value: string) => void;
  cronSettings: any;
  setCronSettings: (settings: any) => void;
}

const ServiceSettings: React.FC<ServiceSettingsProps> = ({
  envSettings, updateEnvField, cronSettings, setCronSettings
}) => {
  return (
    <div className="flex flex-col gap-8" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="card">
        <div className="card-header">
          <h3><Server size={20} /> 外部 API 連携</h3>
        </div>
        <div className="card-body">
          <div className="alert-warning mb-8" style={{ background: 'rgba(255, 193, 7, 0.05)', padding: '16px', borderRadius: '12px', borderLeft: '4px solid var(--warning)', fontSize: '0.9rem' }}>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
              <AlertTriangle size={20} className="text-warning" style={{ flexShrink: 0 }} />
              <div>
                ここでの設定はサーバー上の <code>.env</code> ファイルに直接保存されます。<br/>
                APIキーやトークンが正しくないと、AIレビューやSlack通知が機能しません。
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '2rem' }}>
            <div className="space-y-6" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div className="flex items-center gap-2 mb-2" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Cpu size={18} className="text-primary" />
                <h4 style={{ color: 'var(--text-main)', margin: 0 }}>AI サービス (Gemini)</h4>
              </div>
              <div className="form-group">
                <label>Gemini API Key</label>
                <input 
                  type="password" className="form-control" 
                  value={envSettings.GEMINI_API_KEY || ''} 
                  onChange={(e) => updateEnvField('GEMINI_API_KEY', e.target.value)} 
                  placeholder="AI分析に使用するAPIキーを入力"
                />
              </div>
            </div>

            <div className="space-y-6" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div className="flex items-center gap-2 mb-2" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Bell size={18} className="text-primary" />
                <h4 style={{ color: 'var(--text-main)', margin: 0 }}>通知サービス (Slack)</h4>
              </div>
              <div className="form-group">
                <label>Slack Bot Token (xoxb-...)</label>
                <input 
                  type="password" className="form-control" 
                  value={envSettings.SLACK_BOT_TOKEN || ''} 
                  onChange={(e) => updateEnvField('SLACK_BOT_TOKEN', e.target.value)} 
                  placeholder="xoxb- で始まるトークンを入力"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 定期実行設定 */}
      <div className="card">
        <div className="card-header">
          <h3><Calendar size={20} /> 自動レビュー・定期実行</h3>
        </div>
        <div className="card-body">
          <div className="alert-info mb-8" style={{ background: 'rgba(59, 130, 246, 0.05)', padding: '16px', borderRadius: '12px', borderLeft: '4px solid var(--primary)', fontSize: '0.9rem' }}>
            分析期間に基づき、指定時刻に AI レビューを自動生成し Slack へ通知します。
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '2rem' }}>
            <div className="form-group">
              <label>自動実行の有効化</label>
              <div style={{ marginTop: '8px' }}>
                <button 
                  className={`btn ${cronSettings.enabled ? 'btn-primary' : 'btn-outline'}`}
                  onClick={() => setCronSettings({ ...cronSettings, enabled: !cronSettings.enabled })}
                  style={{ width: '100%', padding: '10px' }}
                >
                  {cronSettings.enabled ? '有効 ✅' : '無効 ❌'}
                </button>
              </div>
            </div>
            
            <div className="form-group">
              <label>実行時刻</label>
              <input 
                type="time" 
                className="form-control" 
                value={cronSettings.time || '23:50'} 
                onChange={(e) => setCronSettings({ ...cronSettings, time: e.target.value })}
                style={{ height: '42px' }}
              />
            </div>
            
            <div className="form-group">
              <label>分析対象の期間</label>
              <select 
                className="form-control" 
                value={cronSettings.timeframe || 'weekly'} 
                onChange={(e) => setCronSettings({ ...cronSettings, timeframe: e.target.value })}
                style={{ height: '42px' }}
              >
                <option value="daily">前日 (daily)</option>
                <option value="weekly">前週 (weekly)</option>
                <option value="monthly">前月 (monthly)</option>
              </select>
            </div>
          </div>

          <div style={{ 
            marginTop: '2rem', 
            padding: '1rem', 
            background: 'rgba(255,255,255,0.02)', 
            borderRadius: '12px', 
            fontSize: '0.9rem', 
            color: 'var(--text-muted)',
            textAlign: 'center',
            border: '1px dashed var(--border)'
          }}>
            次回実行予定: <strong style={{ color: 'var(--text-main)' }}>
              {cronSettings.enabled ? `${cronSettings.time || '23:50'} に ${cronSettings.timeframe || 'weekly'} レビューを生成` : '自動実行はオフです'}
            </strong>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ServiceSettings;
