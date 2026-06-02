import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ExternalLink, Bot, Wallet, TrendingUp, Handshake, List } from 'lucide-react';
import client from '../api/client';
import type { KPI, BudgetActual, AssetTrend, SankeyData, LatestSummary, Transaction } from '../api/client';
import AssetPieChart from '../components/AssetPieChart';
import MonthSelector from '../components/MonthSelector';
import { StatItem } from '../components/StatGroup';
import SankeyChart from '../components/SankeyChart';
import BudgetPacemaker from '../components/BudgetPacemaker';
import BudgetForm from '../components/BudgetForm';
import TopHeader from '../components/TopHeader';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [kpi, setKpi] = useState<KPI | null>(null);
  const [budgetActual, setBudgetActual] = useState<BudgetActual[]>([]);
  const [assetTrend, setAssetTrend] = useState<AssetTrend[]>([]);
  const [sankeyData, setSankeyData] = useState<SankeyData | null>(null);
  const [latestSummary, setLatestSummary] = useState<string>('');
  const [weeklyForm, setWeeklyForm] = useState<string[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [pendingReimbursements, setPendingReimbursements] = useState<any[]>([]);
  
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState('monthly');
  const [currentMonth, setCurrentMonth] = useState(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [
        kpiRes, baRes, assetRes, 
        sankeyRes, summaryRes, formRes, 
        txRes, pendingRes
      ] = await Promise.all([
        client.get<KPI>(`/api/kpi?timeframe=${timeframe}&month=${currentMonth}`),
        client.get<BudgetActual[]>(`/api/budget-actual?timeframe=${timeframe}`),
        client.get<AssetTrend[]>('/api/assets'),
        client.get<SankeyData>('/api/stats/flow'),
        client.get<LatestSummary>('/api/analysis-history/latest-summary'),
        client.get<string[]>('/api/analysis-history/form'),
        client.get<Transaction[]>('/api/transactions?limit=10'),
        client.get<any[]>('/api/reimbursements/pending')
      ]);

      setKpi(kpiRes.data);
      setBudgetActual(baRes.data);
      setAssetTrend(assetRes.data);
      setSankeyData(sankeyRes.data);
      setLatestSummary(summaryRes.data.summary);
      setWeeklyForm(formRes.data);
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
  }, [timeframe, currentMonth]);

  // 固定費と変動費を分離 (現状のAPIレスポンスにis_fixedフラグがないため簡易分類)
  const fixedCategories = ['家賃', '光熱費', '通信費', '保険'];
  const variableExpenses = budgetActual.filter(item => !fixedCategories.includes(item.category));
  const fixedExpenses = budgetActual.filter(item => fixedCategories.includes(item.category));

  const pendingTotal = pendingReimbursements.reduce((sum, item) => sum + (item.pending_amount || 0), 0);

  if (loading && !kpi) {
    return (
      <div className="flex justify-center items-center h-screen" style={{ backgroundColor: 'var(--bg-color)' }}>
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[var(--primary)]"></div>
      </div>
    );
  }

  return (
    <>
      <TopHeader 
        title="ダッシュボード" 
        onRefresh={fetchData} 
        timeframes={['daily', 'weekly', 'monthly', 'yearly']}
        activeTimeframe={timeframe}
        onTimeframeChange={setTimeframe}
        loading={loading}
      />

      <div className="dashboard-grid">
        <div className="col-span-12 flex justify-center md:justify-end mb-2">
          <MonthSelector currentMonth={currentMonth} onChange={setCurrentMonth} />
        </div>

        {/* KPI Cards */}
        <div className="kpi-cards">
          <div className="card kpi-card">
            <StatItem 
              label="合計支出" 
              value={`¥${kpi?.actual.toLocaleString() ?? 0}`} 
              subValue={`予算: ¥${kpi?.budget.toLocaleString() ?? 0}`} 
              colorClass="text-[var(--primary-light)]" 
            />
          </div>
          <div className="card kpi-card">
            <StatItem 
              label="1日平均" 
              value={`¥${Math.round((kpi?.actual ?? 0) / Math.max(1, new Date().getDate())).toLocaleString()}`} 
              subValue="当月実績から算出" 
            />
          </div>
          <div className="card kpi-card">
            <StatItem 
              label="家計スコア" 
              value="85/100" 
              subValue="AIによる総合評価" 
              colorClass="text-[var(--success)]" 
            />
          </div>
          <div className="card kpi-card">
            <span className="text-xs uppercase tracking-widest text-[var(--text-muted)] font-bold mb-3">資産構成</span>
            <div className="w-full h-[100px] mt-2">
              <AssetPieChart data={assetTrend} />
            </div>
          </div>
        </div>

        {/* Budget vs Actual */}
        <section className="card section-budget">
          <div className="card-header">
            <h3><Wallet size={20} /> 予算管理</h3>
          </div>
          <div className="card-body">
            <div className="mb-8">
              <BudgetForm history={weeklyForm} />
            </div>
            <BudgetPacemaker 
              timeframe={timeframe} 
              onTimeframeChange={setTimeframe} 
              variableExpenses={variableExpenses} 
              fixedExpenses={fixedExpenses} 
            />
          </div>
        </section>

        {/* AI Analysis Report */}
        <section className="card section-ai-review">
          <div className="card-header">
            <h3><Bot size={20} /> AI 分析レポート</h3>
            <span className="badge score-good">スコア: 85/100</span>
          </div>
          <div className="card-body">
            <div className="review-summary">
              <p className="font-bold leading-relaxed text-[var(--text-main)]">
                {latestSummary || "まだ分析データがありません。"}
              </p>
            </div>
            <div className="review-actions mt-6">
              <button 
                className="btn-outline btn-small flex items-center gap-2"
                onClick={() => navigate('/ai-review')}
              >
                詳細レポートを読む <ExternalLink size={14} />
              </button>
            </div>
          </div>
        </section>

        {/* Asset Trend / Cash Flow */}
        <section className="card section-assets">
          <div className="card-header">
            <h3><TrendingUp size={20} /> 資産推移 / キャッシュフロー</h3>
          </div>
          <div className="card-body">
            <div className="w-full h-[300px] sm:h-[400px]">
              <SankeyChart data={sankeyData} />
            </div>
          </div>
        </section>

        {/* AI Expense Splitter */}
        <section className="card section-splitter">
          <div className="card-header">
            <h3><Handshake size={20} /> AI 立替・精算</h3>
          </div>
          <div className="card-body">
            <div className="flex justify-between items-end mb-6">
              <div className="text-sm font-bold text-[var(--text-muted)]">精算待ち合計</div>
              <div className="text-2xl font-black text-[var(--warning)]">¥{pendingTotal.toLocaleString()}</div>
            </div>
            <ul className="pending-list">
              {pendingReimbursements.slice(0, 5).map((item, idx) => (
                <li key={idx}>
                  <div className="pending-info">
                    <span className="date">{item.transaction_date?.slice(5) || '00-00'}</span>
                    <span className="desc">{item.comment || item.category}</span>
                  </div>
                  <div className="pending-amount">¥{(item.pending_amount || 0).toLocaleString()}</div>
                </li>
              ))}
              {pendingReimbursements.length === 0 && (
                <li className="text-[var(--text-muted)] text-sm font-medium text-center py-8">
                  精算待ちの項目はありません
                </li>
              )}
            </ul>
            <div className="mt-8">
              <button 
                className="btn-primary w-full btn-small"
                onClick={() => navigate('/expense-splitter')}
              >
                精算管理を開く
              </button>
            </div>
          </div>
        </section>

        {/* Recent Transactions */}
        <section className="card section-transactions">
          <div className="card-header">
            <h3><List size={20} /> 最近の明細</h3>
            <button 
              className="btn-text text-sm flex items-center gap-2"
              onClick={() => navigate('/transactions')}
            >
              すべて表示 <ExternalLink size={14} />
            </button>
          </div>
          <div className="card-body">
            <div className="overflow-x-auto">
              <table className="transaction-table">
                <thead>
                  <tr>
                    <th>日付</th>
                    <th>カテゴリ</th>
                    <th>摘要</th>
                    <th>金額</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.slice(0, 8).map((tx) => (
                    <tr key={tx.transaction_id}>
                      <td className="font-mono text-sm">{tx.transaction_date.slice(5)}</td>
                      <td><span className="badge badge-split">{tx.category}</span></td>
                      <td className="font-medium">{tx.comment || '-'}</td>
                      <td className="font-bold text-right">¥{tx.amount.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </div>
    </>
  );
};

export default Dashboard;
