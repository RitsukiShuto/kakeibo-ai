import React, { useEffect, useState } from 'react';
import { Calendar, FileText } from 'lucide-react';
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
                <div className="badge score-good mb-4">Score: {selectedReview.score}</div>
                <h4 className="mb-2">要約</h4>
                <div className="review-summary mb-4">
                  {selectedReview.summary}
                </div>
                <h4 className="mb-2">詳細レポート</h4>
                <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6, color: 'var(--text-main)', padding: '15px', backgroundColor: 'var(--bg-color)', borderRadius: '8px' }}>
                  {reportContent}
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
