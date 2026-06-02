import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ExternalLink } from 'lucide-react';
import client from '../api/client';
import type { KPI, BudgetActual, AssetTrend, SankeyData, LatestSummary, Transaction } from '../api/client';
import AssetPieChart from '../components/AssetPieChart';
import MonthSelector from '../components/MonthSelector';
import StatGroup, { StatItem } from '../components/StatGroup';
import SankeyChart from '../components/SankeyChart';
import BudgetPacemaker from '../components/BudgetPacemaker';
import BudgetForm from '../components/BudgetForm';

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
      <div className="flex justify-center items-center h-screen bg-slate-950">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-[1100px] mx-auto px-8 py-12 min-h-screen text-slate-100">
      <header className="flex justify-between items-center mb-16 pb-6 border-b border-slate-800">
        <div className="text-2xl font-black tracking-tighter text-indigo-400">Kakeibo-ai</div>
        <MonthSelector currentMonth={currentMonth} onChange={setCurrentMonth} />
      </header>

      {/* Overview (最上部) */}
      <section className="mb-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="md:col-span-3">
            <StatGroup>
              <StatItem 
                label="合計支出" 
                value={`¥${kpi?.actual.toLocaleString() ?? 0}`} 
                subValue={`予算: ¥${kpi?.budget.toLocaleString() ?? 0}`} 
                colorClass="text-indigo-400" 
              />
              <StatItem 
                label="1日平均" 
                value={`¥${Math.round((kpi?.actual ?? 0) / Math.max(1, new Date().getDate())).toLocaleString()}`} 
                subValue="当月実績から算出" 
              />
              <StatItem 
                label="家計スコア" 
                value="85/100" 
                subValue="AIによる総合評価" 
                colorClass="text-emerald-400" 
              />
            </StatGroup>
          </div>
          <div className="flex flex-col justify-center items-center bg-slate-900/50 rounded-[32px] p-4 border border-slate-800">
            <div className="text-[10px] font-bold text-slate-500 mb-2 uppercase tracking-widest">資産構成</div>
            <div className="w-full h-[120px]">
              <AssetPieChart data={assetTrend} />
            </div>
          </div>
        </div>
      </section>

      {/* AI Insights */}
      <section className="mb-16">
        <p className="text-xl font-bold leading-relaxed text-slate-300">
          {latestSummary || "まだ分析データがありません。"}
        </p>
      </section>

      {/* Cash Flow Analysis (Sankey) */}
      <section className="mb-20">
        <h2 className="text-lg font-black mb-8 flex items-center gap-4 text-slate-500 uppercase tracking-widest">
          Cash Flow Analysis
          <div className="flex-1 h-px bg-slate-800"></div>
        </h2>
        <div className="bg-slate-900/30 p-4 rounded-3xl border border-slate-800">
          <SankeyChart data={sankeyData} />
        </div>
      </section>

      {/* Operations (中段) */}
      <section className="mb-20">
        <div className="flex justify-between items-end mb-10">
          <h2 className="text-lg font-black flex items-center gap-4 text-slate-500 uppercase tracking-widest w-full">
            Operations
            <div className="flex-1 h-px bg-slate-800"></div>
          </h2>
        </div>
        
        <div className="mb-8">
          <BudgetForm history={weeklyForm} />
        </div>
        
        <BudgetPacemaker 
          timeframe={timeframe} 
          onTimeframeChange={setTimeframe} 
          variableExpenses={variableExpenses} 
          fixedExpenses={fixedExpenses} 
        />
      </section>

      {/* Recent Transactions & Reimbursements (最下部) */}
      <section className="mb-20">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-16">
          <div>
            <h2 className="text-lg font-black mb-10 flex items-center gap-4 text-slate-500 uppercase tracking-widest">
              Recent Transactions
              <div className="flex-1 h-px bg-slate-800"></div>
            </h2>
            <ul className="divide-y divide-slate-800">
              {transactions.slice(0, 5).map((tx) => (
                <li key={tx.transaction_id} className="py-4 flex justify-between items-center">
                  <div>
                    <div className="text-xs font-bold text-slate-500 mb-1">{tx.transaction_date.slice(5)}</div>
                    <div className="font-bold text-slate-200">{tx.comment || tx.category}</div>
                  </div>
                  <div className="font-black text-slate-100">¥{tx.amount.toLocaleString()}</div>
                </li>
              ))}
            </ul>
            <div className="flex flex-col justify-end mt-6">
              <button 
                className="text-sm font-black text-indigo-400 hover:text-indigo-300 transition-colors text-left flex items-center gap-2"
                onClick={() => navigate('/transactions')}
              >
                すべての明細を表示 <ExternalLink size={14} />
              </button>
            </div>
          </div>
          
          <div>
            <h2 className="text-lg font-black mb-10 flex items-center gap-4 text-slate-500 uppercase tracking-widest">
              Reimbursements
              <div className="flex-1 h-px bg-slate-800"></div>
            </h2>
            <div className="bg-slate-900/50 rounded-2xl p-6 border border-slate-800">
              <div className="flex justify-between items-end mb-6">
                <div className="text-sm font-bold text-slate-400">精算待ち合計</div>
                <div className="text-2xl font-black text-amber-500">¥{pendingTotal.toLocaleString()}</div>
              </div>
              <ul className="space-y-4">
                {pendingReimbursements.slice(0, 3).map((item, idx) => (
                  <li key={idx} className="flex justify-between items-center bg-slate-800/50 p-3 rounded-xl">
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 rounded-full bg-amber-500"></div>
                      <span className="text-sm font-bold text-slate-200">{item.comment || item.category}</span>
                    </div>
                    <span className="font-bold text-slate-100">¥{(item.pending_amount || 0).toLocaleString()}</span>
                  </li>
                ))}
                {pendingReimbursements.length === 0 && (
                  <li className="text-slate-500 text-sm font-medium text-center py-4">精算待ちの項目はありません</li>
                )}
              </ul>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Dashboard;
