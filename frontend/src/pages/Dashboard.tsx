import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { ExternalLink, Wallet, Handshake, List, Sparkles } from 'lucide-react';
import client from '../api/client';
import type { KPI, BudgetActual, AssetTrend, SankeyData, LatestSummary, Transaction, ReimbursementSuggestion, WeeklyFormItem } from '../api/client';
import AssetPieChart from '../components/AssetPieChart';
import MonthSelector from '../components/MonthSelector';
import SankeyChart from '../components/SankeyChart';
import BudgetPacemaker from '../components/BudgetPacemaker';
import WeeklyForm from '../components/WeeklyForm';
import TopHeader from '../components/TopHeader';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [kpi, setKpi] = useState<KPI | null>(null);
  const [budgetActual, setBudgetActual] = useState<BudgetActual[]>([]);
  const [assetTrend, setAssetTrend] = useState<AssetTrend[]>([]);
  const [sankeyData, setSankeyData] = useState<SankeyData | null>(null);
  const [latestSummary, setLatestSummary] = useState<string>('');
  const [weeklyForm, setWeeklyForm] = useState<WeeklyFormItem[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [pendingReimbursements, setPendingReimbursements] = useState<any[]>([]);
  const [reimbursementSuggestions, setReimbursementSuggestions] = useState<ReimbursementSuggestion[]>([]);
  
  const [loading, setLoading] = useState(true);
  const [detectLoading, setDetectLoading] = useState(false);
  const [timeframe, setTimeframe] = useState('monthly');
  const [selectedWeek, setSelectedWeek] = useState<string | undefined>(undefined);
  const [currentMonth, setCurrentMonth] = useState(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });

  const fetchData = useCallback(async (isSilent = false) => {
    if (!isSilent) setLoading(true);
    try {
      const [
        kpiRes, baRes, assetRes, 
        sankeyRes, summaryRes, formRes, 
        txRes, pendingRes
      ] = await Promise.all([
        client.get<KPI>(`/api/kpi?timeframe=${timeframe}&month=${currentMonth}`),
        client.get<BudgetActual[]>(`/api/budget-actual?timeframe=${timeframe}&month=${currentMonth}${selectedWeek ? `&week=${selectedWeek}` : ''}`),
        client.get<AssetTrend[]>('/api/assets'),
        client.get<SankeyData>(`/api/stats/flow?month=${currentMonth}`),
        client.get<LatestSummary>('/api/analysis-history/latest-summary'),
        client.get<WeeklyFormItem[]>(`/api/analysis-history/form?month=${currentMonth}`),
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
      if (!isSilent) setLoading(false);
    }
  }, [timeframe, currentMonth, selectedWeek]);

  const fetchAIContent = useCallback(async () => {
    setDetectLoading(true);
    try {
      const detectRes = await client.post<ReimbursementSuggestion[]>('/api/expense-splitter/detect');
      setReimbursementSuggestions(detectRes.data);
    } catch (error) {
      console.error('Failed to fetch AI suggestions', error);
    } finally {
      setDetectLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    fetchAIContent();
  }, [fetchAIContent]);

  // APIの'section'フィールドを使用して固定費と変動費を分離
  const variableExpenses = budgetActual.filter(item => item.section === 'variable');
  const fixedExpenses = budgetActual.filter(item => item.section === 'fixed');

  const pendingTotal = pendingReimbursements.reduce((sum, item) => sum + (item.pending_amount || 0), 0);

  const handleWeekClick = (startDate: string) => {
    setTimeframe('weekly');
    setSelectedWeek(startDate);
  };

  const handleMonthChange = (newMonth: string) => {
    setCurrentMonth(newMonth);
    setSelectedWeek(undefined); // 月が変わったら週選択をクリア
  };

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
        onRefresh={() => fetchData(false)} 
        loading={loading}
      />

      <div className="max-w-[1400px] mx-auto px-4 sm:px-6 py-8 md:py-12 text-slate-100">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end mb-8 md:mb-16 gap-4">
          <h2 className="text-2xl font-bold tracking-tight text-slate-400">Overview</h2>
          <MonthSelector currentMonth={currentMonth} onChange={handleMonthChange} />
        </div>

        {/* Overview Section */}
        <section className="grid grid-cols-12 gap-8 md:gap-12 items-center mb-16 md:mb-24">
          <div className="col-span-12 lg:col-span-8 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8">
            <div className="flex flex-col">
              <span className="text-xs uppercase tracking-widest text-slate-500 font-bold mb-2">Total Expense</span>
              <span className="text-5xl sm:text-6xl md:text-7xl font-black text-indigo-500 tracking-tighter transition-all">
                ¥{kpi?.actual.toLocaleString() ?? 0}
              </span>
              <span className="text-sm text-slate-500 font-bold mt-2">Budget: ¥{kpi?.budget.toLocaleString() ?? 0}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs uppercase tracking-widest text-slate-500 font-bold mb-2">Daily Average</span>
              <span className="text-4xl sm:text-5xl md:text-6xl font-black text-slate-100 tracking-tighter transition-all">
                ¥{Math.round((kpi?.actual ?? 0) / Math.max(1, new Date().getDate())).toLocaleString()}
              </span>
              <span className="text-sm text-slate-500 font-bold mt-2">Selected Month</span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs uppercase tracking-widest text-slate-500 font-bold mb-2">Kakeibo Score</span>
              <span className="text-5xl sm:text-6xl md:text-7xl font-black text-emerald-500 tracking-tighter transition-all">
                85
              </span>
              <span className="text-sm text-slate-500 font-bold mt-2">Out of 100</span>
            </div>
          </div>
          <div className="col-span-12 lg:col-span-4 h-[240px]">
            <AssetPieChart data={assetTrend} />
          </div>
        </section>

        <hr className="border-slate-800 mb-16 md:mb-24" />

        {/* AI Analysis Report */}
        <section className="mb-16 md:mb-24">
          <div className="mb-6">
            <h3 className="text-sm font-black text-slate-500 uppercase tracking-[0.2em]">AI Insights</h3>
            <div className="h-px bg-slate-800 mt-2"></div>
          </div>
          <div>
            <p className="text-lg md:text-xl italic text-slate-300 leading-relaxed max-w-4xl">
              {latestSummary || "まだ分析データがありません。"}
            </p>
          </div>
        </section>

        {/* Asset Trend / Cash Flow */}
        <section className="mb-16 md:mb-24">
          <div className="mb-6">
            <h3 className="text-sm font-black text-slate-500 uppercase tracking-[0.2em]">Cash Flow</h3>
            <div className="h-px bg-slate-800 mt-2"></div>
          </div>
          <div className="w-full h-[300px] md:h-[450px]">
            <SankeyChart data={sankeyData} />
          </div>
        </section>

        <div className="grid grid-cols-12 gap-8 md:gap-16 mb-16 md:mb-24">
          {/* Budget vs Actual (Operations Part 1) */}
          <section className="col-span-12 lg:col-span-6">
            <div className="flex items-center gap-3 mb-8">
              <Wallet className="text-amber-500" size={24} />
              <h3 className="text-xl font-bold">予算管理</h3>
            </div>
            <div>
              <div className="mb-8 md:mb-12">
                <WeeklyForm 
                  history={weeklyForm} 
                  selectedWeek={selectedWeek}
                  onWeekClick={handleWeekClick}
                />
              </div>
              <BudgetPacemaker 
                timeframe={timeframe} 
                onTimeframeChange={(tf) => {
                  setTimeframe(tf);
                  if (tf !== 'weekly') setSelectedWeek(undefined);
                }} 
                variableExpenses={variableExpenses} 
                fixedExpenses={fixedExpenses} 
              />
            </div>
          </section>

          {/* Recent Transactions (Operations Part 2) */}
          <section className="col-span-12 lg:col-span-6">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-3">
                <List className="text-slate-400" size={24} />
                <h3 className="text-xl font-bold font-mono tracking-tight uppercase">Recent</h3>
              </div>
              <button 
                className="text-indigo-400 hover:text-indigo-300 text-xs font-bold flex items-center gap-1 group"
                onClick={() => navigate('/transactions')}
              >
                VIEW ALL <ExternalLink size={12} className="group-hover:translate-x-0.5 transition-transform" />
              </button>
            </div>
            
            <div className="flex flex-col space-y-px">
              {transactions.slice(0, 10).map((tx) => (
                <div key={tx.transaction_id} className="flex items-center justify-between py-2 border-b border-slate-900/50 hover:bg-slate-800/20 px-2 rounded-sm transition-colors group">
                  <div className="flex items-center gap-4 md:gap-6">
                    <span className="text-[10px] font-mono text-slate-500 w-8 md:w-10">{tx.transaction_date.slice(5)}</span>
                    <span className="px-1.5 py-0.5 text-[9px] font-black uppercase tracking-tighter bg-indigo-500/5 text-indigo-400/70 border border-indigo-500/10 rounded-sm">
                      {tx.category}
                    </span>
                  </div>
                  <span className="text-sm font-bold text-slate-100 font-mono group-hover:text-indigo-400 transition-colors">¥{tx.amount.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* Reimbursements (Bottom Section) */}
        <section className="mb-16 md:mb-24">
          <div className="mb-8 md:mb-12">
            <h3 className="text-sm font-black text-slate-500 uppercase tracking-[0.2em]">Reimbursements</h3>
            <div className="h-px bg-slate-800 mt-2"></div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 md:gap-16">
            {/* Pending List */}
            <div>
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                  <Handshake className="text-indigo-400" size={20} />
                  <h4 className="text-lg font-bold">精算待ち</h4>
                </div>
                <div className="text-2xl font-black text-amber-500">¥{pendingTotal.toLocaleString()}</div>
              </div>
              
              <ul className="space-y-2">
                {pendingReimbursements.slice(0, 5).map((item, idx) => (
                  <li key={idx} className="flex items-center justify-between p-3 bg-slate-900/30 rounded-lg border border-slate-800/50">
                    <div className="flex flex-col">
                      <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">{item.transaction_date || '00-00'}</span>
                      <span className="font-bold text-slate-200">{item.comment || item.category}</span>
                    </div>
                    <div className="text-lg font-bold text-amber-500 font-mono">¥{(item.pending_amount || 0).toLocaleString()}</div>
                  </li>
                ))}
                {pendingReimbursements.length === 0 && (
                  <li className="text-slate-600 text-sm font-medium text-center py-10 bg-slate-900/20 rounded-lg border border-dashed border-slate-800">
                    精算待ちの項目はありません
                  </li>
                )}
              </ul>
              <button 
                className="w-full mt-6 py-3 border border-slate-800 hover:bg-slate-800/50 text-slate-400 hover:text-slate-100 text-xs font-black uppercase tracking-widest rounded-lg transition-all"
                onClick={() => navigate('/expense-splitter')}
              >
                Manage All
              </button>
            </div>

            {/* AI Detection Suggestions */}
            <div>
              <div className="flex items-center gap-3 mb-8">
                <Sparkles className="text-amber-400" size={20} />
                <h4 className="text-lg font-bold">AI 立替検知</h4>
                {detectLoading && <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-amber-400"></div>}
              </div>
              
              <div className="space-y-2">
                {reimbursementSuggestions.length > 0 ? (
                  reimbursementSuggestions.slice(0, 5).map((suggestion) => {
                    const tx = transactions.find(t => t.transaction_id === suggestion.transaction_id);
                    return (
                      <div key={suggestion.transaction_id} className="p-3 bg-indigo-500/5 border border-indigo-500/20 rounded-lg flex items-start justify-between">
                        <div className="flex flex-col gap-1">
                          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">Potential Split</span>
                          <span className="text-sm font-bold text-slate-200">{tx?.comment || tx?.category || 'Unknown'}</span>
                          <p className="text-xs text-slate-500 italic">"{suggestion.reason}"</p>
                        </div>
                        <div className="flex flex-col items-end gap-2">
                          <span className="text-sm font-black text-indigo-400 font-mono">¥{tx?.amount.toLocaleString()}</span>
                          <button 
                            className="px-2 py-1 bg-indigo-500 hover:bg-indigo-400 text-white text-[10px] font-black uppercase rounded shadow-lg shadow-indigo-500/20 transition-all"
                            onClick={() => navigate('/expense-splitter')}
                          >
                            Mark
                          </button>
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="text-slate-600 text-sm font-medium text-center py-10 bg-slate-900/20 rounded-lg border border-dashed border-slate-800">
                    {detectLoading ? "立替候補をスキャン中..." : "新しい立替候補は見つかりませんでした"}
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>
      </div>
    </>
  );
};

export default Dashboard;
