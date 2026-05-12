import React, { useState, useEffect } from 'react';
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, AreaChart, Area } from 'recharts';
import { Target, Wallet, TrendingUp, AlertCircle, ChevronRight, Settings as SettingsIcon, Sparkles, RefreshCw } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import client from '../api/client';
import TopHeader from '../components/TopHeader';

const LifePlan: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [advice, setAdvice] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [adviceLoading, setAdviceLoading] = useState(false);
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

  const fetchAdvice = async () => {
    setAdviceLoading(true);
    setAdvice(null);
    try {
      const res = await client.get('/api/life-plan/advice');
      setAdvice(res.data.advice);
    } catch (err) {
      console.error('Failed to fetch AI advice', err);
      setAdvice('アドバイスの生成に失敗しました。💅💦');
    } finally {
      setAdviceLoading(false);
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

  if (error || !data || !data.trajectory) {
    return (
      <>
        <TopHeader title="ライフプラン・シミュレーション" />
        <div className="p-6">
          <div className="card bg-danger/10 border-danger/20 p-6 flex flex-col items-center gap-4 text-center">
            <AlertCircle size={48} className="text-danger" />
            <div>
              <h3 className="text-xl font-bold mb-2">設定またはデータの取得に失敗しました</h3>
              <p className="text-muted mb-4">{error || 'シミュレーションデータが空です。'}</p>
              <a href="/settings" className="btn-primary inline-flex items-center gap-2">
                <SettingsIcon size={18} /> 設定画面へ
              </a>
            </div>
          </div>
        </div>
      </>
    );
  }

  const { trajectory, settings } = data;
  const lastAsset = trajectory.length > 0 ? trajectory[trajectory.length - 1].assets : 0;
  const isBankrupt = trajectory.some((t: any) => t.assets < 0);
  const retirementYear = trajectory.find((t: any) => t.is_retired);

  return (
    <>
      <TopHeader title="ライフプラン・シミュレーション" onRefresh={fetchSimulation} />
      
      <div className="page-content">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Main Chart Area */}
          <div className="lg:col-span-2 flex flex-col gap-8">
            <div className="card">
              <div className="card-header flex justify-between items-center">
                <h3><TrendingUp size={20} /> 資産推移予測 (100歳まで)</h3>
                <div className="text-xs text-muted">※運用利回り {settings?.annual_return_rate || 0}% / インフレ {settings?.annual_inflation_rate || 0}%</div>
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

            {/* AI Advice Card - Large format if advice is present */}
            {advice && (
              <div className="card" style={{ border: '1px solid var(--primary)', background: 'rgba(59, 130, 246, 0.05)' }}>
                <div className="card-header flex justify-between items-center">
                  <h3 className="flex items-center gap-2"><Sparkles size={20} className="text-primary" /> AIの長期診断・アドバイス</h3>
                  <button 
                    onClick={fetchAdvice} 
                    disabled={adviceLoading}
                    className="text-xs flex items-center gap-1 text-primary hover:opacity-80 transition-opacity"
                  >
                    <RefreshCw size={14} className={adviceLoading ? 'animate-spin' : ''} /> 再診断
                  </button>
                </div>
                <div className="card-body">
                  <div className="markdown-content">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {advice}
                    </ReactMarkdown>
                  </div>
                  <div className="flex justify-end mt-4">
                    <a href="/ai-chat" className="text-xs text-primary flex items-center gap-1 font-bold">
                      詳しくチャットで相談する <ChevronRight size={14} />
                    </a>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Sidebar Area */}
          <div className="flex flex-col gap-8">
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
                    現在の月間貯蓄額: {(settings?.monthly_savings || 0).toLocaleString()}円<br/>
                    引退後の月間生活費: {(settings?.monthly_living_expenses_post_retirement || 0).toLocaleString()}円<br/>
                    引退予定年齢: {settings?.retirement_age || '--'}歳
                  </div>
                </div>
              </div>
            </div>

            {/* AI Advice Call-to-action if no advice yet */}
            {!advice && (
              <div className="card" style={{ border: '1px dashed var(--primary)', background: 'rgba(59, 130, 246, 0.02)' }}>
                <div className="card-body py-8 flex flex-col items-center text-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                    <Sparkles size={24} />
                  </div>
                  <div>
                    <h4 className="font-bold mb-1">AIによる将来診断</h4>
                    <p className="text-xs text-muted">シミュレーション結果に基づき、AIが長期的な家計のアドバイスを生成します。</p>
                  </div>
                  <button 
                    onClick={fetchAdvice} 
                    disabled={adviceLoading}
                    className="btn-primary w-full flex items-center justify-center gap-2"
                  >
                    {adviceLoading ? (
                      <>
                        <RefreshCw size={18} className="animate-spin" />
                        分析中...
                      </>
                    ) : (
                      <>
                        <Sparkles size={18} />
                        診断を開始する
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}

            <div className="card">
              <div className="card-header">
                <h3><Wallet size={20} /> ライフイベント</h3>
              </div>
              <div className="card-body p-0">
                <div className="max-h-[300px] overflow-y-auto">
                  <table className="table" style={{ fontSize: '0.85rem' }}>
                    <thead style={{ position: 'sticky', top: 0, background: 'var(--card-bg)', zIndex: 1 }}>
                      <tr>
                        <th>年齢</th>
                        <th>イベント</th>
                        <th className="text-right">額</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(settings?.events || []).map((e: any, idx: number) => (
                        <tr key={idx}>
                          <td>{e.age}歳</td>
                          <td className="truncate max-w-[100px]">{e.name}</td>
                          <td className="text-right text-danger">-{Math.round(e.amount/10000)}万</td>
                        </tr>
                      ))}
                      {(!settings?.events || settings.events.length === 0) && (
                        <tr>
                          <td colSpan={3} className="text-center text-muted py-4">設定なし</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
                <div className="p-4 border-t border-border">
                  <a href="/settings" className="text-xs text-muted flex items-center gap-1 hover:text-primary transition-colors">
                    <SettingsIcon size={14} /> 設定から編集する
                  </a>
                </div>
              </div>
            </div>
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
        
        .markdown-content {
          font-size: 0.95rem;
          line-height: 1.7;
          color: var(--text-main);
        }
        .markdown-content h1, .markdown-content h2, .markdown-content h3 {
          margin-top: 1.5rem;
          margin-bottom: 1rem;
          font-weight: bold;
        }
        .markdown-content h3 { font-size: 1.1rem; border-left: 4px solid var(--primary); padding-left: 12px; }
        .markdown-content p { margin-bottom: 1rem; }
        .markdown-content ul, .markdown-content ol { margin-bottom: 1rem; padding-left: 1.5rem; }
        .markdown-content li { margin-bottom: 0.5rem; }
        .markdown-content strong { color: var(--primary); }
        .markdown-content table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; }
        .markdown-content th, .markdown-content td { border: 1px solid var(--border); padding: 8px; text-align: left; }
        .markdown-content th { background: rgba(255,255,255,0.05); }
      `}</style>
    </>
  );
};

export default LifePlan;
