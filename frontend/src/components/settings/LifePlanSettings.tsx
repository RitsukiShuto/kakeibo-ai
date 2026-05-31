import React from 'react';
import { TrendingUp, Wallet, Plus, Trash2 } from 'lucide-react';

interface LifePlanSettingsProps {
  profile: any;
  updateProfileField: (path: string, value: any) => void;
}

const LifePlanSettings: React.FC<LifePlanSettingsProps> = ({ profile, updateProfileField }) => {
  return (
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
  );
};

export default LifePlanSettings;
