import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ExternalLink, Wallet, Handshake, List } from 'lucide-react';
import client from '../api/client';
import type { KPI, BudgetActual, AssetTrend, SankeyData, LatestSummary, Transaction } from '../api/client';
import AssetPieChart from '../components/AssetPieChart';
import MonthSelector from '../components/MonthSelector';
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

      <div className="max-w-[1400px] mx-auto px-6 py-12 text-slate-100">
        <div className="flex justify-between items-end mb-16">
          <h2 className="text-2xl font-bold tracking-tight text-slate-400">Overview</h2>
          <MonthSelector currentMonth={currentMonth} onChange={setCurrentMonth} />
        </div>

        {/* Overview Section */}
        <section className="grid grid-cols-12 gap-12 items-center mb-24">
          <div className="col-span-12 lg:col-span-8 grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="flex flex-col">
              <span className="text-xs uppercase tracking-widest text-slate-500 font-bold mb-2">Total Expense</span>
              <span className="text-7xl font-black text-indigo-500 tracking-tighter">
                ¥{kpi?.actual.toLocaleString() ?? 0}
              </span>
              <span className="text-sm text-slate-500 font-bold mt-2">Budget: ¥{kpi?.budget.toLocaleString() ?? 0}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs uppercase tracking-widest text-slate-500 font-bold mb-2">Daily Average</span>
              <span className="text-6xl font-black text-slate-100 tracking-tighter">
                ¥{Math.round((kpi?.actual ?? 0) / Math.max(1, new Date().getDate())).toLocaleString()}
              </span>
              <span className="text-sm text-slate-500 font-bold mt-2">Current Month</span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs uppercase tracking-widest text-slate-500 font-bold mb-2">Kakeibo Score</span>
              <span className="text-7xl font-black text-emerald-500 tracking-tighter">
                85
              </span>
              <span className="text-sm text-slate-500 font-bold mt-2">Out of 100</span>
            </div>
          </div>
          <div className="col-span-12 lg:col-span-4 h-[240px]">
            <AssetPieChart data={assetTrend} />
          </div>
        </section>

        <hr className="border-slate-800 mb-24" />

        <div className="grid grid-cols-12 gap-16">
          {/* Budget vs Actual */}
          <section className="col-span-12 lg:col-span-6 mb-24">
            <div className="flex items-center gap-3 mb-8">
              <Wallet className="text-amber-500" size={24} />
              <h3 className="text-xl font-bold">予算管理</h3>
            </div>
            <div>
              <div className="mb-12">
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
          <section className="col-span-12 lg:col-span-6 mb-24">
            <div className="mb-6">
              <h3 className="text-sm font-black text-slate-500 uppercase tracking-[0.2em]">AI Insights</h3>
              <div className="h-px bg-slate-800 mt-2"></div>
            </div>
            <div>
              <p className="text-lg italic text-slate-300 leading-relaxed">
                {latestSummary || "まだ分析データがありません。"}
              </p>
            </div>
          </section>

          {/* Asset Trend / Cash Flow */}
          <section className="col-span-12 mb-24">
            <div className="mb-6">
              <h3 className="text-sm font-black text-slate-500 uppercase tracking-[0.2em]">Cash Flow</h3>
              <div className="h-px bg-slate-800 mt-2"></div>
            </div>
            <div className="w-full h-[450px]">
              <SankeyChart data={sankeyData} />
            </div>
          </section>

          {/* AI Expense Splitter */}
          <section className="col-span-12 lg:col-span-5 mb-24">
            <div className="flex items-center gap-3 mb-8">
              <Handshake className="text-indigo-400" size={24} />
              <h3 className="text-xl font-bold">AI 立替・精算</h3>
            </div>
            <div>
              <div className="flex justify-between items-end mb-8">
                <div className="text-sm font-bold text-slate-500 uppercase tracking-wider">精算待ち合計</div>
                <div className="text-4xl font-black text-amber-500">¥{pendingTotal.toLocaleString()}</div>
              </div>
              <ul className="divide-y divide-slate-800">
                {pendingReimbursements.slice(0, 5).map((item, idx) => (
                  <li key={idx} className="flex items-center justify-between py-4">
                    <div className="flex flex-col">
                      <span className="text-xs font-mono text-slate-500">{item.transaction_date?.slice(5) || '00-00'}</span>
                      <span className="font-bold text-slate-200">{item.comment || item.category}</span>
                    </div>
                    <div className="text-xl font-bold text-amber-500 font-mono">¥{(item.pending_amount || 0).toLocaleString()}</div>
                  </li>
                ))}
                {pendingReimbursements.length === 0 && (
                  <li className="text-slate-500 text-sm font-medium text-center py-12">
                    精算待ちの項目はありません
                  </li>
                )}
              </ul>
              <div className="mt-12">
                <button 
                  className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-lg transition-all shadow-lg shadow-indigo-500/20"
                  onClick={() => navigate('/expense-splitter')}
                >
                  精算管理を開く
                </button>
              </div>
            </div>
          </section>

          {/* Recent Transactions */}
          <section className="col-span-12 lg:col-span-7 mb-24">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-3">
                <List className="text-slate-400" size={24} />
                <h3 className="text-xl font-bold">最近の明細</h3>
              </div>
              <button 
                className="text-indigo-400 hover:text-indigo-300 text-sm font-bold flex items-center gap-2"
                onClick={() => navigate('/transactions')}
              >
                すべて表示 <ExternalLink size={14} />
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-800">
                    <th className="py-4 font-bold text-slate-500 text-xs uppercase tracking-widest">日付</th>
                    <th className="py-4 font-bold text-slate-500 text-xs uppercase tracking-widest">カテゴリ</th>
                    <th className="py-4 font-bold text-slate-500 text-xs uppercase tracking-widest">摘要</th>
                    <th className="py-4 font-bold text-slate-500 text-xs uppercase tracking-widest text-right">金額</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {transactions.slice(0, 8).map((tx) => (
                    <tr key={tx.transaction_id} className="hover:bg-slate-800/30 transition-colors group">
                      <td className="py-4 font-mono text-sm text-slate-400">{tx.transaction_date.slice(5)}</td>
                      <td className="py-4">
                        <span className="px-2 py-1 text-[10px] font-black uppercase tracking-tighter bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded">
                          {tx.category}
                        </span>
                      </td>
                      <td className="py-4 font-medium text-slate-200">{tx.comment || '-'}</td>
                      <td className="py-4 font-bold text-right text-slate-100">¥{tx.amount.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      </div>
    </>
  );
};

export default Dashboard;
