import React, { useState, useEffect } from 'react';
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, AreaChart, Area } from 'recharts';
import { Target, Wallet, TrendingUp, AlertCircle, Info, ChevronRight, Settings as SettingsIcon } from 'lucide-react';
import client from '../api/client';
import TopHeader from '../components/TopHeader';

const LifePlan: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSimulation = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await client.get('/api/life-plan/simulation');
      setData(res.data);
    } catch (err: any) {
      console.error('Failed to fetch life plan', err);
      setError(err.response?.data?.detail || 'シミュレーションの取得に失敗しました。設定を確認してください。');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSimulation();
  }, []);

  const formatYAxis = (value: number) => {
    if (value >= 100000000) return `${(value / 100000000).toFixed(1)}億円`;
    if (value >= 10000) return `${(value / 10000).toLocaleString()}万円`;
    return value.toLocaleString();
  };

  if (loading) {
    return (
      <>
        <TopHeader title="ライフプラン・シミュレーション" />
        <div className="flex items-center justify-center h-64">
          <div className="text-xl text-muted animate-pulse">将来を予測中...💅✨</div>
        </div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <TopHeader title="ライフプラン・シミュレーション" />
        <div className="p-6">
          <div className="card bg-danger/10 border-danger/20 p-6 flex flex-col items-center gap-4 text-center">
            <AlertCircle size={48} className="text-danger" />
            <div>
              <h3 className="text-xl font-bold mb-2">設定が必要です</h3>
              <p className="text-muted mb-4">{error}</p>
              <a href="/settings" className="btn-primary inline-flex items-center gap-2">
                <SettingsIcon size={18} /> 設定画面へ
              </a>
            </div>
          </div>
        </div>
      </>
    );
  }

  const { trajectory, advice, settings } = data;
  const lastAsset = trajectory[trajectory.length - 1].assets;
  const isBankrupt = trajectory.some((t: any) => t.assets < 0);
  const retirementYear = trajectory.find((t: any) => t.is_retired);

  return (
    <>
      <TopHeader title="ライフプラン・シミュレーション" onRefresh={fetchSimulation} />
      
      <div className="page-content">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="card lg:col-span-2">
            <div className="card-header flex justify-between items-center">
              <h3><TrendingUp size={20} /> 資産推移予測 (100歳まで)</h3>
              <div className="text-xs text-muted">※運用利回り {settings.annual_return_rate}% / インフレ {settings.annual_inflation_rate}%</div>
            </div>
            <div className="card-body" style={{ height: '400px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trajectory} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorAssets" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                  <XAxis 
                    dataKey="age" 
                    unit="歳" 
                    axisLine={false} 
                    tickLine={false}
                    tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                  />
                  <YAxis 
                    tickFormatter={formatYAxis} 
                    axisLine={false} 
                    tickLine={false}
                    tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                  />
                  <Tooltip 
                    formatter={(value: any) => [formatYAxis(Number(value)), '推定資産']}
                    labelFormatter={(label) => `${label}歳`}
                    contentStyle={{ backgroundColor: 'var(--card-bg)', borderColor: 'var(--border)', borderRadius: '8px' }}
                  />
                  {retirementYear && (
                    <ReferenceLine x={retirementYear.age} stroke="var(--warning)" strokeDasharray="3 3" label={{ position: 'top', value: '引退', fill: 'var(--warning)', fontSize: 12 }} />
                  )}
                  <ReferenceLine y={0} stroke="var(--danger)" />
                  <Area 
                    type="monotone" 
                    dataKey="assets" 
                    stroke="var(--primary)" 
                    strokeWidth={3}
                    fillOpacity={1} 
                    fill="url(#colorAssets)" 
                    animationDuration={1500}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="flex flex-col gap-6">
            <div className="card">
              <div className="card-header">
                <h3><Target size={20} /> シミュレーション概況</h3>
              </div>
              <div className="card-body">
                <div className="flex flex-col gap-4">
                  <div className="kpi-item">
                    <div className="text-sm text-muted">100歳時の推定資産</div>
                    <div className={`text-2xl font-bold ${lastAsset >= 0 ? 'text-success' : 'text-danger'}`}>
                      {formatYAxis(lastAsset)}
                    </div>
                  </div>
                  <div className="kpi-item">
                    <div className="text-sm text-muted">老後の資金繰り</div>
                    <div className="flex items-center gap-2 mt-1">
                      {isBankrupt ? (
                        <span className="badge badge-danger">枯渇の恐れあり</span>
                      ) : (
                        <span className="badge badge-success">安泰予測</span>
                      )}
                    </div>
                  </div>
                  <div className="divider"></div>
                  <div className="text-xs text-muted leading-relaxed">
                    現在の月間貯蓄額: {(settings.monthly_savings || 0).toLocaleString()}円<br/>
                    引退後の月間生活費: {settings.monthly_living_expenses_post_retirement.toLocaleString()}円<br/>
                    引退予定年齢: {settings.retirement_age}歳
                  </div>
                </div>
              </div>
            </div>

            <div className="card" style={{ border: '1px solid var(--primary)', background: 'rgba(59, 130, 246, 0.05)' }}>
              <div className="card-header">
                <h3><Info size={20} className="text-primary" /> AIの長期診断</h3>
              </div>
              <div className="card-body">
                <div className="text-sm leading-relaxed whitespace-pre-wrap" style={{ maxHeight: '200px', overflowY: 'auto' }}>
                  {advice}
                </div>
                <a href="/ai-chat" className="mt-4 text-xs text-primary flex items-center justify-end gap-1 font-bold">
                  詳しくチャットで相談する <ChevronRight size={14} />
                </a>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3><Wallet size={20} /> ライフイベントの設定</h3>
          </div>
          <div className="card-body">
            <table className="table">
              <thead>
                <tr>
                  <th>発生年齢</th>
                  <th>イベント名</th>
                  <th className="text-right">予定支出額</th>
                </tr>
              </thead>
              <tbody>
                {settings.events.map((e: any, idx: number) => (
                  <tr key={idx}>
                    <td>{e.age}歳</td>
                    <td>{e.name}</td>
                    <td className="text-right text-danger">-{e.amount.toLocaleString()}円</td>
                  </tr>
                ))}
                {settings.events.length === 0 && (
                  <tr>
                    <td colSpan={3} className="text-center text-muted py-4">設定されたイベントはありません</td>
                  </tr>
                )}
              </tbody>
            </table>
            <p className="mt-4 text-xs text-muted">
              ※これらの設定は「設定 ＞ プロフィール ＞ Advanced(JSON)」から編集できます。
            </p>
          </div>
        </div>
      </div>

      <style>{`
        .badge {
          padding: 4px 12px;
          border-radius: 999px;
          font-size: 0.75rem;
          font-weight: bold;
        }
        .badge-success { background: rgba(16, 185, 129, 0.2); color: #10b981; }
        .badge-danger { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
        .divider { height: 1px; background: var(--border); margin: 8px 0; }
      `}</style>
    </>
  );
};

export default LifePlan;
