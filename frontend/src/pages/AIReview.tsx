import React, { useEffect, useState } from 'react';
import { Info, AlertTriangle, AlertCircle, CheckCircle, Bot, ChevronRight } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import client from '../api/client';
import type { AnalysisHistory, UsageStat } from '../api/client';

// モデル別の固定カラーパレット
const MODEL_COLORS: Record<string, string> = {
  'gemini-2.0-flash': '#6366f1',
  'gemini-1.5-flash': '#8b5cf6',
  'gemini-1.5-pro': '#a78bfa',
  'gemini-2.5-flash': '#4f46e5',
  'unknown': '#475569',
};
const fallbackColors = ['#06b6d4', '#10b981', '#f59e0b', '#ef4444'];
const getModelColor = (model: string, index: number) =>
  MODEL_COLORS[model] ?? fallbackColors[index % fallbackColors.length];

const AIReview: React.FC = () => {
  const [history, setHistory] = useState<AnalysisHistory[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [reportContent, setReportContent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState('monthly');
  const [usageStats, setUsageStats] = useState<UsageStat[]>([]);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await client.get<AnalysisHistory[]>(`/api/analysis-history?timeframe=${timeframe}`);
      setHistory(res.data);
      if (res.data.length > 0) {
        setSelectedId(res.data[0].id);
      } else {
        setSelectedId(null);
        setReportContent('');
      }
    } catch (error) {
      console.error('Failed to fetch analysis history', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchReportContent = async (id: number) => {
    setReportContent('読み込み中...');
    try {
      const res = await client.get<{ content: string }>(`/api/analysis-history/${id}/content`);
      setReportContent(res.data.content);
    } catch (error) {
      console.error('Failed to fetch report content', error);
      setReportContent('レポートの読み込みに失敗しました。ファイルが存在しない可能性があります。');
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [timeframe]);

  useEffect(() => {
    if (selectedId !== null) {
      fetchReportContent(selectedId);
    }
  }, [selectedId]);

  useEffect(() => {
    client.get<UsageStat[]>('/api/analysis-history/usage-stats?months=6')
      .then(res => setUsageStats(res.data))
      .catch(() => {});
  }, []);

  const selectedReview = history.find(h => h.id === selectedId);
  const pastReviews = history.filter(h => h.id !== selectedId);

  // 月別チャート用にピボット変換（モデルを列方向に展開）
  const models = [...new Set(usageStats.map(s => s.model))];
  const months = [...new Set(usageStats.map(s => s.month))].sort();
  const chartData = months.map(month => {
    const row: Record<string, string | number> = { month };
    models.forEach(model => {
      const entry = usageStats.find(s => s.month === month && s.model === model);
      row[model] = entry ? entry.total_tokens : 0;
    });
    return row;
  });

  return (
    <div className="max-w-[1100px] mx-auto px-8 py-12 min-h-screen text-slate-100">
      <header className="flex justify-between items-center mb-16 pb-6 border-b border-slate-800">
        <div className="text-2xl font-black tracking-tighter text-indigo-400">AI Review</div>
        <div className="flex bg-slate-900 border border-slate-800 rounded-full p-1">
          {['daily', 'weekly', 'monthly'].map((tf) => (
            <button 
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-4 py-1.5 rounded-full text-xs font-bold tracking-widest uppercase transition-colors ${timeframe === tf ? 'bg-indigo-600 text-white' : 'text-slate-500 hover:text-slate-300'}`}
            >
              {tf}
            </button>
          ))}
        </div>
      </header>

      {loading && !selectedReview ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
        </div>
      ) : history.length === 0 ? (
        <div className="text-center p-12 text-slate-500 font-medium bg-slate-900/30 rounded-3xl border border-slate-800">
          この期間のレポート履歴はありません。
        </div>
      ) : (
        <>
          {/* Model Usage Chart */}
          {usageStats.length > 0 && (
            <section className="mb-20">
              <h2 className="text-lg font-black mb-10 flex items-center gap-4 text-slate-500 uppercase tracking-widest">
                Model Usage
                <div className="flex-1 h-px bg-slate-800"></div>
              </h2>
              <div className="bg-slate-900/50 rounded-3xl p-8 border border-slate-800">
                <div className="flex items-center justify-between mb-6">
                  <p className="text-sm text-slate-400">直近6ヶ月のモデル別トークン使用量</p>
                  <div className="flex items-center gap-3 text-xs text-slate-500">
                    <span>合計: {usageStats.reduce((s, r) => s + r.total_tokens, 0).toLocaleString()} tokens</span>
                    <span>•</span>
                    <span>分析数: {usageStats.reduce((s, r) => s + r.count, 0)} 件</span>
                  </div>
                </div>
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={chartData} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="month" tick={{ fill: '#64748b', fontSize: 11 }} />
                    <YAxis tick={{ fill: '#64748b', fontSize: 11 }} tickFormatter={(v: number) => v >= 1000 ? `${(v / 1000).toFixed(0)}k` : String(v)} />
                    <Tooltip
                      contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8 }}
                      labelStyle={{ color: '#94a3b8', fontWeight: 700 }}
                      formatter={(value: unknown, name: unknown) => [`${Number(value).toLocaleString()} tokens`, String(name ?? '')]}
                    />
                    <Legend wrapperStyle={{ color: '#64748b', fontSize: 11 }} />
                    {models.map((model, i) => (
                      <Bar key={model} dataKey={model} stackId="a" fill={getModelColor(model, i)} radius={i === models.length - 1 ? [4, 4, 0, 0] : [0, 0, 0, 0]} />
                    ))}
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </section>
          )}

          {/* Main Selected Report */}
          {selectedReview && (
            <section className="mb-20">
              <h2 className="text-lg font-black mb-10 flex items-center gap-4 text-slate-500 uppercase tracking-widest">
                Selected Analysis
                <div className="flex-1 h-px bg-slate-800"></div>
              </h2>
              
              <div className="bg-slate-900/50 rounded-3xl p-8 border border-slate-800">
                <div className="flex justify-between items-start mb-8 pb-8 border-b border-slate-800/50">
                  <div>
                    <div className="text-sm font-bold text-slate-500 mb-2 uppercase tracking-widest">{selectedReview.timeframe} Report</div>
                    <div className="text-3xl font-black text-slate-100">{selectedReview.created_at.split(' ')[0]}</div>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <div className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-4 py-2 rounded-xl text-lg font-black tracking-wider">
                      SCORE: {selectedReview.score}
                    </div>
                    {selectedReview.total_tokens && (
                      <div className="text-xs text-slate-500 flex items-center gap-1">
                        <Bot size={12} /> {selectedReview.model_name || 'AI'} ({selectedReview.total_tokens.toLocaleString()} tk)
                      </div>
                    )}
                  </div>
                </div>

                <div className="mb-10">
                  <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-4">Summary</h3>
                  <p className="text-xl font-bold leading-relaxed text-slate-300">
                    {selectedReview.summary}
                  </p>
                </div>

                <div>
                  <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-4">Detail</h3>
                  <div className="prose prose-invert prose-slate max-w-none 
                    prose-headings:text-indigo-400 prose-headings:font-black 
                    prose-p:text-slate-300 prose-p:leading-relaxed 
                    prose-a:text-indigo-400 hover:prose-a:text-indigo-300 
                    prose-strong:text-slate-200 prose-strong:font-black 
                    prose-ul:text-slate-300 prose-ol:text-slate-300
                    prose-blockquote:border-l-indigo-500 prose-blockquote:bg-indigo-500/5 prose-blockquote:py-1 prose-blockquote:px-4 prose-blockquote:rounded-r-lg prose-blockquote:not-italic prose-blockquote:text-slate-300"
                  >
                    <ReactMarkdown 
                      remarkPlugins={[remarkGfm]}
                      components={{
                        blockquote(props: any) {
                          const { node, children } = props;
                          try {
                            const pNode = node.children?.find((n: any) => n.type === 'element' && n.tagName === 'p');
                            if (pNode && pNode.children && pNode.children.length > 0) {
                              const textNode = pNode.children[0];
                              if (textNode.type === 'text' && textNode.value.startsWith('[!')) {
                                const match = textNode.value.match(/^\[!(\w+)\](?:[ \t]*(.*))?/);
                                if (match) {
                                  const type = match[1].toUpperCase();
                                  const titleText = match[2] || type.charAt(0) + type.slice(1).toLowerCase();
                                  
                                  let Icon = Info;
                                  let colorClass = 'text-indigo-400';
                                  let bgClass = 'bg-indigo-500/10 border-l-indigo-500';
                                  
                                  if (type === 'WARNING' || type === 'CAUTION') {
                                    Icon = AlertTriangle; colorClass = 'text-amber-400'; bgClass = 'bg-amber-500/10 border-l-amber-500';
                                  } else if (type === 'DANGER' || type === 'ERROR') {
                                    Icon = AlertCircle; colorClass = 'text-rose-400'; bgClass = 'bg-rose-500/10 border-l-rose-500';
                                  } else if (type === 'SUCCESS' || type === 'TIP' || type === 'DONE') {
                                    Icon = CheckCircle; colorClass = 'text-emerald-400'; bgClass = 'bg-emerald-500/10 border-l-emerald-500';
                                  }
                        
                                  const lines = textNode.value.split('\n');
                                  lines.shift(); 
                                  const newText = lines.join('\n');
                                  
                                  const modifiedChildren = React.Children.map(children, (child, index) => {
                                    if (index === 0 && React.isValidElement(child)) {
                                       const childProps = child.props as any;
                                       const newPChildren = React.Children.map(childProps.children, (pChild, pIndex) => {
                                         if (pIndex === 0 && typeof pChild === 'string') {
                                            return newText;
                                         }
                                         return pChild;
                                       });
                                       return React.cloneElement(child, {}, newPChildren);
                                    }
                                    return child;
                                  });
                        
                                  return (
                                    <div className={`my-6 pl-4 py-3 pr-4 border-l-4 rounded-r-xl ${bgClass}`}>
                                      <div className={`flex items-center gap-2 font-bold mb-2 ${colorClass}`}>
                                        <Icon size={18} />
                                        <span>{titleText}</span>
                                      </div>
                                      <div className="text-slate-300 opacity-90 m-0">
                                        {modifiedChildren}
                                      </div>
                                    </div>
                                  );
                                }
                              }
                            }
                          } catch (e) {}
                          
                          return <blockquote {...props} />;
                        }
                      }}
                    >
                      {reportContent}
                    </ReactMarkdown>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Past Reports Grid */}
          {pastReviews.length > 0 && (
            <section className="mb-20">
              <h2 className="text-lg font-black mb-10 flex items-center gap-4 text-slate-500 uppercase tracking-widest">
                Past Reviews
                <div className="flex-1 h-px bg-slate-800"></div>
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {pastReviews.map((h) => (
                  <div 
                    key={h.id}
                    onClick={() => {
                      setSelectedId(h.id);
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    }}
                    className="bg-slate-900/30 border border-slate-800 rounded-2xl p-6 cursor-pointer hover:bg-slate-800/50 hover:border-slate-700 transition-all group flex flex-col h-full"
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <div className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">{h.timeframe}</div>
                        <div className="text-lg font-black text-slate-200 group-hover:text-indigo-400 transition-colors">{h.created_at.split(' ')[0]}</div>
                      </div>
                      <div className="bg-slate-800/50 text-slate-300 px-3 py-1 rounded-lg text-sm font-bold border border-slate-700">
                        {h.score}
                      </div>
                    </div>
                    
                    <div className="text-sm text-slate-400 line-clamp-3 mb-6 flex-1">
                      {h.summary}
                    </div>
                    
                    <div className="flex justify-end mt-auto">
                      <div className="text-indigo-400 text-sm font-bold flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        詳細を見る <ChevronRight size={16} />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
};

export default AIReview;
