import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Scale, ChartArea, Bot, List, Handshake, ExternalLink } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import client from '../api/client';
import type { KPI, BudgetActual, AssetTrend, AnalysisHistory, Transaction } from '../api/client';
import KPICard from '../components/KPICard';
import ProgressBar from '../components/ProgressBar';
import AssetChart from '../components/AssetChart';
import TopHeader from '../components/TopHeader';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [kpi, setKpi] = useState<KPI | null>(null);
  const [budgetActual, setBudgetActual] = useState<BudgetActual[]>([]);
  const [assetTrend, setAssetTrend] = useState<AssetTrend[]>([]);
  const [history, setHistory] = useState<AnalysisHistory[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [pendingReimbursements, setPendingReimbursements] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState('monthly');
  const [assetTimeframe, setAssetTimeframe] = useState<'1m' | '3m' | '6m' | '1y' | 'all'>('all');

  const fetchData = async () => {
    setLoading(true);
    try {
      const [kpiRes, baRes, assetRes, histRes, txRes, pendingRes] = await Promise.all([
        client.get<KPI>('/api/kpi'),
        client.get<BudgetActual[]>('/api/budget-actual'),
        client.get<AssetTrend[]>('/api/assets'),
        client.get<AnalysisHistory[]>(`/api/analysis-history?timeframe=${timeframe}`),
        client.get<Transaction[]>('/api/transactions?limit=10'),
        client.get<any[]>('/api/reimbursements/pending')
      ]);

      setKpi(kpiRes.data);
      setBudgetActual(baRes.data);
      setAssetTrend(assetRes.data);
      setHistory(histRes.data);
      setTransactions(txRes.data);
      setPendingReimbursements(pendingRes.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [timeframe]);

  const latestReview = history.length > 0 ? history[0] : null;

  return (
    <>
      <TopHeader 
        title="ダッシュボード" 
        onRefresh={fetchData} 
        timeframes={['daily', 'weekly', 'monthly']}
        activeTimeframe={timeframe}
        onTimeframeChange={setTimeframe}
      />
      
      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
          <div className="spinner">読み込み中...</div>
        </div>
      ) : (
        <div className="dashboard-grid">
          {/* KPI Cards */}
          <div className="kpi-cards">
            <KPICard title="予算" value={`${kpi?.budget.toLocaleString() ?? 0}円`} />
            <KPICard title="実支出" value={`${kpi?.actual.toLocaleString() ?? 0}円`} />
            <KPICard 
              title="残額" 
              value={`${kpi?.remaining.toLocaleString() ?? 0}円`} 
              trendType={kpi && kpi.remaining > 0 ? 'positive' : 'negative'} 
            />
            <KPICard title="総資産" value={`${kpi?.total_assets.toLocaleString() ?? 0}円`} />
          </div>

          {/* Budget vs Actual */}
          <div className="card section-budget">
            <div className="card-header">
              <h3><Scale size={20} /> 予実管理 (カテゴリ別)</h3>
            </div>
            <div className="card-body">
              {budgetActual.length > 0 ? (
                budgetActual.map((item) => (
                  <ProgressBar 
                    key={item.category}
                    label={item.category}
                    actual={item.actual}
                    budget={item.budget}
                  />
                ))
              ) : (
                <div className="text-muted">データがありません。</div>
              )}
            </div>
          </div>

          {/* AI Review */}
          <div className="card section-ai-review">
            <div className="card-header">
              <h3><Bot size={20} /> {timeframe === 'daily' ? '日次' : timeframe === 'weekly' ? '週次' : '月次'}分析レポート</h3>
            </div>
            <div className="card-body">
              {latestReview ? (
                <>
                  <div className="badge score-good mb-2">ととのいスコア: {latestReview.score}</div>
                  <div className="review-date">{new Date(latestReview.created_at).toLocaleDateString()}</div>
                  <div className="review-summary markdown-content">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {latestReview.summary}
                    </ReactMarkdown>
                  </div>
                  <button className="btn-outline btn-small mt-3" onClick={() => navigate('/ai-review')}>
                    全文レポートを開く <ExternalLink size={14} />
                  </button>
                </>
              ) : (
                <div className="text-muted">この期間のレポートはまだありません。</div>
              )}
            </div>
          </div>

          {/* Asset Trend */}
          <div className="card section-assets">
            <div className="card-header">
              <h3><ChartArea size={20} /> 資産推移</h3>
              <div className="timeframe-tabs" style={{ fontSize: '0.7rem' }}>
                {['1m', '3m', '6m', '1y', 'all'].map((tf) => (
                  <button 
                    key={tf} 
                    className={`tab-btn ${assetTimeframe === tf ? 'active' : ''}`}
                    onClick={() => setAssetTimeframe(tf as any)}
                    style={{ padding: '4px 8px' }}
                  >
                    {tf.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
            <div className="card-body">
              <AssetChart data={assetTrend} timeframe={assetTimeframe} />
            </div>
          </div>

          {/* Pending Reimbursements */}
          <div className="card section-splitter">
            <div className="card-header">
              <h3><Handshake size={20} /> 精算待ちの立替金</h3>
            </div>
            <div className="card-body">
              {pendingReimbursements.length > 0 ? (
                <ul className="pending-list">
                  {pendingReimbursements.map((tx) => (
                    <li key={tx.transaction_id}>
                      <div className="pending-info">
                        <span className="date">{tx.transaction_date.slice(5)}</span>
                        <span className="desc">{tx.comment || tx.category}</span>
                      </div>
                      <div className="pending-amount">{tx.pending_amount.toLocaleString()}円</div>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-muted">精算待ちの項目はありません。✨</div>
              )}
              <button className="btn-text w-100 mt-4" onClick={() => navigate('/expense-splitter')}>
                すべての立替を管理
              </button>
            </div>
          </div>

          {/* Recent Transactions */}
          <div className="card section-transactions">
            <div className="card-header">
              <h3><List size={20} /> 最近の明細</h3>
            </div>
            <div className="card-body">
              <ul className="pending-list">
                {transactions.slice(0, 5).map((tx) => (
                  <li key={tx.transaction_id}>
                    <div className="pending-info">
                      <span className="date">{tx.transaction_date.slice(5)}</span>
                      <span className="desc">{tx.comment || tx.category}</span>
                    </div>
                    <div className="pending-amount">{tx.amount.toLocaleString()}円</div>
                  </li>
                ))}
              </ul>
              <button className="btn-text w-100 mt-4" onClick={() => navigate('/transactions')}>
                すべての明細を表示
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Dashboard;
