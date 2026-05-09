import React, { useEffect, useState } from 'react';
import { Scale, ChartArea, Bot, List } from 'lucide-react';
import client from '../api/client';
import type { KPI, BudgetActual, AssetTrend, AnalysisHistory, Transaction } from '../api/client';
import KPICard from '../components/KPICard';
import ProgressBar from '../components/ProgressBar';
import AssetChart from '../components/AssetChart';
import TopHeader from '../components/TopHeader';

const Dashboard: React.FC = () => {
  const [kpi, setKpi] = useState<KPI | null>(null);
  const [budgetActual, setBudgetActual] = useState<BudgetActual[]>([]);
  const [assetTrend, setAssetTrend] = useState<AssetTrend[]>([]);
  const [history, setHistory] = useState<AnalysisHistory[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [kpiRes, baRes, assetRes, histRes, txRes] = await Promise.all([
        client.get<KPI>('/api/kpi'),
        client.get<BudgetActual[]>('/api/budget-actual'),
        client.get<AssetTrend[]>('/api/assets'),
        client.get<AnalysisHistory[]>('/api/analysis-history'),
        client.get<Transaction[]>('/api/transactions?limit=10')
      ]);

      setKpi(kpiRes.data);
      setBudgetActual(baRes.data);
      setAssetTrend(assetRes.data);
      setHistory(histRes.data);
      setTransactions(txRes.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const latestReview = history.length > 0 ? history[0] : null;

  return (
    <>
      <TopHeader title="ダッシュボード" onRefresh={fetchData} />
      
      <div className="dashboard-grid">
        {/* KPI Cards */}
        <div className="kpi-cards">
          <KPICard title="予算 (Budget)" value={`${kpi?.budget.toLocaleString() ?? 0}円`} />
          <KPICard title="実支出 (Actual)" value={`${kpi?.actual.toLocaleString() ?? 0}円`} />
          <KPICard title="残額 (Remaining)" value={`${kpi?.remaining.toLocaleString() ?? 0}円`} trendType={kpi && kpi.remaining > 0 ? 'positive' : 'negative'} />
          <KPICard title="総資産 (Total Assets)" value={`${kpi?.total_assets.toLocaleString() ?? 0}円`} />
        </div>

        {/* Budget vs Actual */}
        <div className="card section-budget">
          <div className="card-header">
            <h3><Scale size={20} /> 予実管理 (カテゴリ別)</h3>
          </div>
          <div className="card-body">
            {budgetActual.map((item) => (
              <ProgressBar 
                key={item.category}
                label={item.category}
                actual={item.actual}
                budget={item.budget}
              />
            ))}
          </div>
        </div>

        {/* AI Review */}
        <div className="card section-ai-review">
          <div className="card-header">
            <h3><Bot size={20} /> AI 分析レポート</h3>
          </div>
          <div className="card-body">
            {latestReview ? (
              <>
                <div className="badge score-good mb-2">Score: {latestReview.score}</div>
                <div className="review-date">{latestReview.created_at}</div>
                <div className="review-summary">
                  {latestReview.summary}
                </div>
                <button className="btn-outline btn-small">レポート全文を表示</button>
              </>
            ) : (
              <div className="text-muted">レポートがありません。</div>
            )}
          </div>
        </div>

        {/* Asset Trend */}
        <div className="card section-assets">
          <div className="card-header">
            <h3><ChartArea size={20} /> 資産推移</h3>
          </div>
          <div className="card-body">
            <AssetChart data={assetTrend} />
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="card section-splitter">
          <div className="card-header">
            <h3><List size={20} /> 最近の明細</h3>
          </div>
          <div className="card-body">
            <ul className="pending-list">
              {transactions.slice(0, 5).map((tx) => (
                <li key={tx.transaction_id}>
                  <div className="pending-info">
                    <span className="date">{tx.transaction_date}</span>
                    <span className="desc">{tx.comment || tx.category}</span>
                  </div>
                  <div className="pending-amount">{tx.amount.toLocaleString()}円</div>
                </li>
              ))}
            </ul>
            <button className="btn-text w-100 mt-4">すべての明細を表示</button>
          </div>
        </div>
      </div>
    </>
  );
};

export default Dashboard;
