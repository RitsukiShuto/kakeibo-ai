import React, { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { ExternalLink } from 'lucide-react';
import client from '../api/client';
import type { KPI, BudgetActual, AssetTrend, AnalysisHistory, Transaction } from '../api/client';
import ProgressBar from '../components/ProgressBar';
import AssetChart from '../components/AssetChart';
import AssetPieChart from '../components/AssetPieChart';
import MonthSelector from '../components/MonthSelector';
import StatGroup, { StatItem } from '../components/StatGroup';

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
  const [currentMonth, setCurrentMonth] = useState(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [kpiRes, baRes, assetRes, histRes, txRes, pendingRes] = await Promise.all([
        client.get<KPI>(`/api/kpi?timeframe=${timeframe}&month=${currentMonth}`),
        client.get<BudgetActual[]>(`/api/budget-actual?month=${currentMonth}`),
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
  }, [timeframe, currentMonth]);

  // ペースメーカー計算ロジック
  const paceData = useMemo(() => {
    const now = new Date();
    const currentYear = now.getFullYear();
    const currentMonthNum = now.getMonth() + 1;
    const [selYear, selMonth] = currentMonth.split('-').map(Number);
    
    // 選択された月が未来ならペースは0、過去なら100%
    if (selYear > currentYear || (selYear === currentYear && selMonth > currentMonthNum)) {
      return { todayLimitRatio: 0 };
    }
    if (selYear < currentYear || (selYear === currentYear && selMonth < currentMonthNum)) {
      return { todayLimitRatio: 1 };
    }

    const daysInMonth = new Date(selYear, selMonth, 0).getDate();
    const dayOfMonth = now.getDate();
    return {
      todayLimitRatio: dayOfMonth / daysInMonth
    };
  }, [currentMonth]);

  const latestReview = history.length > 0 ? history[0] : null;
  
  // 固定費と変動費を分離 (現状のAPIレスポンスにis_fixedフラグがあると仮定、なければ簡易分類)
  const fixedCategories = ['家賃', '光熱費', '通信費', '保険'];
  const variableExpenses = budgetActual.filter(item => !fixedCategories.includes(item.category));
  const fixedExpenses = budgetActual.filter(item => fixedCategories.includes(item.category));

  const pendingTotal = pendingReimbursements.reduce((sum, item) => sum + (item.pending_amount || 0), 0);
  const dailyLimit = kpi ? Math.max(0, (kpi.budget - kpi.actual) / Math.max(1, 30 * (1 - paceData.todayLimitRatio))) : 0;

  if (loading && !kpi) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-[1100px] mx-auto px-8 py-12 bg-white min-h-screen">
      <header className="flex justify-between items-center mb-16 pb-6 border-b border-slate-100">
        <div className="text-2xl font-black tracking-tighter text-indigo-600">Kakeibo-ai</div>
        <MonthSelector currentMonth={currentMonth} onChange={setCurrentMonth} />
      </header>

      {/* AI Advice Area */}
      <section className="mb-16">
        <div className="inline-block px-3 py-1 bg-indigo-600 text-white rounded text-[10px] font-black mb-4">AIアドバイス</div>
        <p className="text-2xl font-bold leading-tight text-slate-800">
          {latestReview?.summary || "今月も順調に家計管理が進んでいますね！"}
        </p>
      </section>

      {/* Main Stats */}
      <StatGroup>
        <StatItem 
          label="今日使える額" 
          value={`¥${Math.round(dailyLimit).toLocaleString()}`} 
          subValue="1日あたりの自由枠目安" 
          colorClass="text-indigo-600" 
        />
        <StatItem 
          label="総資産" 
          value={`¥${kpi?.total_assets.toLocaleString() ?? 0}`} 
          subValue="▲ ¥15,000 (前月比)" 
        />
        <StatItem 
          label="精算待ち" 
          value={`¥${pendingTotal.toLocaleString()}`} 
          subValue={`未精算 ${pendingReimbursements.length}件`} 
          colorClass="text-amber-500" 
        />
      </StatGroup>

      {/* Budget Management */}
      <section className="mb-20">
        <div className="flex gap-1 mb-8 border-b border-slate-100 pb-2">
          {[
            { id: 'daily', label: '日次' },
            { id: 'weekly', label: '週次' },
            { id: 'monthly', label: '月次' },
            { id: 'quarterly', label: '四半期' },
            { id: 'yearly', label: '年次' }
          ].map(t => (
            <button 
              key={t.id} 
              onClick={() => setTimeframe(t.id)}
              className={`px-6 py-2 text-xs font-black rounded-md transition-colors ${timeframe === t.id ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:bg-slate-50'}`}
            >
              {t.label}
            </button>
          ))}
        </div>

        <div className="mb-16">
          <h2 className="text-lg font-black mb-10 flex items-center gap-4 text-slate-400 uppercase tracking-widest">
            変動費の予実管理 
            <div className="flex-1 h-px bg-slate-100"></div>
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-16 gap-y-2">
            {variableExpenses.length > 0 ? (
              variableExpenses.map(item => (
                <ProgressBar 
                  key={item.category}
                  label={item.category}
                  actual={item.actual}
                  budget={item.budget}
                  paceLimit={item.budget * paceData.todayLimitRatio}
                  showDiff={true}
                />
              ))
            ) : (
              <div className="text-slate-400 font-medium">データがありません。</div>
            )}
          </div>
        </div>

        <div>
          <h2 className="text-lg font-black mb-10 flex items-center gap-4 text-slate-400 uppercase tracking-widest">
            固定費の状況 
            <div className="flex-1 h-px bg-slate-100"></div>
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-16 gap-y-2">
            {fixedExpenses.length > 0 ? (
              fixedExpenses.map(item => (
                <ProgressBar 
                  key={item.category}
                  label={item.category}
                  actual={item.actual}
                  budget={item.budget}
                />
              ))
            ) : (
              <div className="text-slate-400 font-medium">データがありません。</div>
            )}
          </div>
        </div>
      </section>

      {/* Asset Analysis */}
      <section className="mb-20">
        <h2 className="text-lg font-black mb-10 flex items-center gap-4 text-slate-400 uppercase tracking-widest">
          資産分析 
          <div className="flex-1 h-px bg-slate-100"></div>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-16">
          <div className="md:col-span-2">
            <div className="text-[10px] font-bold text-slate-400 mb-6 uppercase tracking-widest">資産推移</div>
            <AssetChart data={assetTrend} timeframe="all" />
          </div>
          <div>
            <div className="text-[10px] font-bold text-slate-400 mb-6 uppercase tracking-widest">資産内訳</div>
            <div className="aspect-square flex items-center justify-center bg-slate-50 rounded-[32px] border-2 border-dashed border-slate-100 p-4">
              <AssetPieChart data={assetTrend} />
            </div>
          </div>
        </div>
      </section>

      {/* Recent Activity */}
      <section className="mb-20">
        <h2 className="text-lg font-black mb-10 flex items-center gap-4 text-slate-400 uppercase tracking-widest">
          最近の支出 
          <div className="flex-1 h-px bg-slate-100"></div>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-16">
          <ul className="divide-y divide-slate-50">
            {transactions.slice(0, 5).map((tx) => (
              <li key={tx.transaction_id} className="py-4 flex justify-between items-center">
                <div>
                  <div className="text-xs font-bold text-slate-400 mb-1">{tx.transaction_date.slice(5)}</div>
                  <div className="font-bold text-slate-700">{tx.comment || tx.category}</div>
                </div>
                <div className="font-black text-slate-900">¥{tx.amount.toLocaleString()}</div>
              </li>
            ))}
          </ul>
          <div className="flex flex-col justify-end pb-4">
            <button 
              className="text-sm font-black text-indigo-600 hover:text-indigo-400 transition-colors text-left flex items-center gap-2"
              onClick={() => navigate('/transactions')}
            >
              すべての明細を表示 <ExternalLink size={14} />
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Dashboard;
