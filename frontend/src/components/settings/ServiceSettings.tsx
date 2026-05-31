import React from 'react';
import { Server, AlertTriangle, Eye, TrendingUp } from 'lucide-react';

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
    <div className="card">
      <div className="card-header">
        <h3><Server size={20} /> 外部サービス連携（初期設定）</h3>
      </div>
      <div className="card-body">
        <div className="alert-warning mb-6" style={{ background: 'rgba(255, 193, 7, 0.1)', padding: '16px', borderRadius: '8px', borderLeft: '4px solid var(--warning)', fontSize: '0.9rem' }}>
          <AlertTriangle size={16} className="inline mr-2" />
          ここでの設定はサーバー上の <code>.env</code> ファイルに直接保存されます。変更には十分注意してください。
        </div>

        <div className="dashboard-grid" style={{ padding: 0, gap: '2rem' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <h4 style={{ color: 'var(--primary)', borderBottom: '1px solid var(--border)', paddingBottom: '8px' }}>
              MoneyForward 連携
            </h4>
            <div className="form-group">
              <label>MF ユーザーID (Email)</label>
              <input 
                type="text" className="form-control" 
                value={envSettings.MF_USER_ID || ''} 
                onChange={(e) => updateEnvField('MF_USER_ID', e.target.value)} 
              />
            </div>
            <div className="form-group">
              <label>MF パスワード</label>
              <div style={{ position: 'relative' }}>
                <input 
                  type="password" className="form-control" 
                  id="mf-password-input"
                  value={envSettings.MF_PASSWORD || ''} 
                  onChange={(e) => updateEnvField('MF_PASSWORD', e.target.value)} 
                />
                <button 
                  className="btn-icon" 
                  style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', opacity: 0.5 }}
                  onClick={() => {
                    const el = document.getElementById('mf-password-input') as HTMLInputElement;
                    el.type = el.type === 'password' ? 'text' : 'password';
                  }}
                >
                  <Eye size={18} />
                </button>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <h4 style={{ color: 'var(--primary)', borderBottom: '1px solid var(--border)', paddingBottom: '8px' }}>
              AI & 通知設定
            </h4>
            <div className="form-group">
              <label>Gemini API Key</label>
              <input 
                type="text" className="form-control" 
                value={envSettings.GEMINI_API_KEY || ''} 
                onChange={(e) => updateEnvField('GEMINI_API_KEY', e.target.value)} 
              />
            </div>
            <div className="form-group">
              <label>Slack Bot Token (xoxb-...)</label>
              <input 
                type="text" className="form-control" 
                value={envSettings.SLACK_BOT_TOKEN || ''} 
                onChange={(e) => updateEnvField('SLACK_BOT_TOKEN', e.target.value)} 
              />
            </div>
          </div>
        </div>

        {/* 定期実行設定 */}
        <div className="card mt-6">
          <div className="card-header">
            <h3><TrendingUp size={20} /> 定期実行設定</h3>
          </div>
          <div className="card-body">
            <div className="alert-info mb-6" style={{ background: 'rgba(59, 130, 246, 0.1)', padding: '16px', borderRadius: '8px', borderLeft: '4px solid var(--primary)', fontSize: '0.9rem' }}>
              <AlertTriangle size={16} className="inline mr-2" />
              毎日の自動レビュー実行に関する設定です。変更は <code>settings.json</code> に保存されます。
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <label style={{ marginBottom: 0, minWidth: '120px' }}>自動実行</label>
                <button 
                  className={`btn ${cronSettings.enabled ? 'btn-primary' : 'btn-outline'}`}
                  onClick={() => setCronSettings({ ...cronSettings, enabled: !cronSettings.enabled })}
                  style={{ minWidth: '100px' }}
                >
                  {cronSettings.enabled ? '有効 ✅' : '無効 ❌'}
                </button>
              </div>
              <div className="form-group">
                <label>実行時刻</label>
                <input 
                  type="time" 
                  className="form-control" 
                  value={cronSettings.time || '23:50'} 
                  onChange={(e) => setCronSettings({ ...cronSettings, time: e.target.value })}
                  style={{ maxWidth: '200px' }}
                />
              </div>
              <div className="form-group">
                <label>分析期間</label>
                <select 
                  className="form-control" 
                  value={cronSettings.timeframe || 'weekly'} 
                  onChange={(e) => setCronSettings({ ...cronSettings, timeframe: e.target.value })}
                  style={{ maxWidth: '200px' }}
                >
                  <option value="daily">毎日 (daily)</option>
                  <option value="weekly">毎週 (weekly)</option>
                  <option value="monthly">毎月 (monthly)</option>
                </select>
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '8px' }}>
                次回実行予定: <strong>{cronSettings.enabled ? `毎日 ${cronSettings.time || '23:50'} (${cronSettings.timeframe || 'weekly'}レビュー)` : '停止中'}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ServiceSettings;
