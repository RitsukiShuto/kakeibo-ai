import React, { useEffect, useState } from 'react';
import { Calendar, FileText, Info, AlertTriangle, AlertCircle, CheckCircle, Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import client from '../api/client';
import type { AnalysisHistory } from '../api/client';
import TopHeader from '../components/TopHeader';

const AIReview: React.FC = () => {
  const [history, setHistory] = useState<AnalysisHistory[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [reportContent, setReportContent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState('monthly');

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

  const selectedReview = history.find(h => h.id === selectedId);

  return (
    <>
      <TopHeader 
        title="AI 分析レポート" 
        onRefresh={fetchHistory} 
        timeframes={['daily', 'weekly', 'monthly']}
        activeTimeframe={timeframe}
        onTimeframeChange={setTimeframe}
      />
      
      <div className="dashboard-grid">
        {/* History List */}
        <div className="card section-splitter">
          <div className="card-header">
            <h3><Calendar size={20} /> {timeframe === 'daily' ? '日次' : timeframe === 'weekly' ? '週次' : '月次'}分析履歴</h3>
          </div>
          <div className="card-body" style={{ padding: 0 }}>
            {loading ? (
              <div className="p-4 text-center">読み込み中...</div>
            ) : history.length > 0 ? (
              <ul className="history-list">
                {history.map((h) => (
                  <li 
                    key={h.id} 
                    className={selectedId === h.id ? 'active' : ''} 
                    onClick={() => setSelectedId(h.id)}
                    style={selectedId === h.id ? { backgroundColor: 'var(--bg-color)', borderLeft: '4px solid var(--primary)' } : {}}
                  >
                    <div className="flex justify-between items-center" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div className="font-bold" style={{ fontWeight: 'bold' }}>{h.created_at.split(' ')[0]}</div>
                        <div className="text-muted text-sm" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{h.timeframe}</div>
                      </div>
                      <div className="badge score-good">Score: {h.score}</div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="p-8 text-center text-muted">この期間のレポート履歴はありません。</div>
            )}
          </div>
        </div>

        {/* Report Detail */}
        <div className="card section-assets">
          <div className="card-header">
            <h3><FileText size={20} /> レポート詳細</h3>
          </div>
          <div className="card-body">
            {selectedReview ? (
              <div className="review-full-text">
                <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '16px' }}>
                  <div className="badge score-good">Score: {selectedReview.score}</div>
                  {selectedReview.total_tokens && (
                    <div className="badge" style={{ backgroundColor: 'rgba(0,0,0,0.2)', border: '1px solid var(--border)', color: 'var(--text-muted)' }}>
                      <Bot size={14} className="inline mr-1" />
                      {selectedReview.model_name || 'AI Model'} ({selectedReview.total_tokens.toLocaleString()} tokens)
                    </div>
                  )}
                </div>
                <h4 className="mb-2">要約</h4>
                <div className="review-summary mb-4">
                  {selectedReview.summary}
                </div>
                <h4 className="mb-2">詳細レポート</h4>
                <div className="markdown-content" style={{ color: 'var(--text-main)', padding: '20px', backgroundColor: 'rgba(0,0,0,0.2)', borderRadius: '8px', border: '1px solid var(--border)' }}>
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
                                let colorVar = 'var(--primary)';
                                let bgColor = 'rgba(59, 130, 246, 0.1)';
                                
                                if (type === 'WARNING' || type === 'CAUTION') {
                                  Icon = AlertTriangle; colorVar = 'var(--warning)'; bgColor = 'rgba(245, 158, 11, 0.1)';
                                } else if (type === 'DANGER' || type === 'ERROR') {
                                  Icon = AlertCircle; colorVar = 'var(--danger)'; bgColor = 'rgba(239, 68, 68, 0.1)';
                                } else if (type === 'SUCCESS' || type === 'TIP' || type === 'DONE') {
                                  Icon = CheckCircle; colorVar = 'var(--success)'; bgColor = 'rgba(16, 185, 129, 0.1)';
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
                                  <div style={{
                                    borderLeft: `4px solid ${colorVar}`,
                                    backgroundColor: bgColor,
                                    padding: '12px 16px',
                                    margin: '16px 0',
                                    borderRadius: '0 8px 8px 0'
                                  }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: colorVar, fontWeight: 'bold', marginBottom: '8px', fontSize: '0.95rem' }}>
                                      <Icon size={18} />
                                      <span>{titleText}</span>
                                    </div>
                                    <div style={{ margin: 0, opacity: 0.9 }}>
                                      {modifiedChildren}
                                    </div>
                                  </div>
                                );
                              }
                            }
                          }
                        } catch (e) {
                          // Fallback to normal rendering on error
                        }
                        
                        return <blockquote style={{ borderLeft: '4px solid var(--border)', paddingLeft: '16px', color: 'var(--text-muted)', margin: '16px 0' }} {...props} />;
                      }
                    }}
                  >
                    {reportContent}
                  </ReactMarkdown>
                </div>
              </div>
            ) : (
              <div className="text-muted">レポートを選択してください。</div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default AIReview;
