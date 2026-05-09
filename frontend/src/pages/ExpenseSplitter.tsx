import React, { useEffect, useState } from 'react';
import { Handshake, Zap, CheckCircle2 } from 'lucide-react';
import client from '../api/client';
import type { Transaction, ReimbursementSuggestion } from '../api/client';
import TopHeader from '../components/TopHeader';

const ExpenseSplitter: React.FC = () => {
  const [pending, setPending] = useState<any[]>([]);
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [, setLoading] = useState(false);
  const [detecting, setDetecting] = useState(false);
  
  const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([]);
  const [selectedTxId, setSelectedTxId] = useState<string>('');
  const [aiInput, setAiInput] = useState('');
  const [selfAmt, setSelfAmt] = useState<number>(0);
  const [parsing, setParsing] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [pendingRes, recentRes] = await Promise.all([
        client.get<any[]>('/api/reimbursements/pending'),
        client.get<Transaction[]>('/api/transactions?limit=20')
      ]);
      setPending(pendingRes.data);
      setRecentTransactions(recentRes.data);
    } catch (error) {
      console.error('Failed to fetch splitter data', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleDetect = async () => {
    setDetecting(true);
    try {
      const res = await client.post<ReimbursementSuggestion[]>('/api/expense-splitter/detect');
      setSuggestions(res.data);
    } catch (error) {
      console.error('Detection failed', error);
    } finally {
      setDetecting(false);
    }
  };

  const handleApplySuggestion = async (id: string) => {
    const tx = recentTransactions.find(t => t.transaction_id === id);
    if (!tx) return;
    
    try {
      await client.put(`/api/transactions/${id}`, {
        is_reimbursement: 1,
        self_amount: Math.floor(tx.amount / 2),
        reimbursement_status: 'pending'
      });
      setSuggestions(suggestions.filter(s => s.transaction_id !== id));
      fetchData();
    } catch (error) {
      console.error('Failed to apply suggestion', error);
    }
  };

  const handleAiParse = async () => {
    const tx = recentTransactions.find(t => t.transaction_id === selectedTxId);
    if (!tx || !aiInput) return;

    setParsing(true);
    try {
      const res = await client.post('/api/expense-splitter/parse', {
        text: aiInput,
        total_amount: tx.amount
      });
      if (res.data && res.data.self_amount !== undefined) {
        setSelfAmt(res.data.self_amount);
      }
    } catch (error) {
      console.error('AI parsing failed', error);
    } finally {
      setParsing(false);
    }
  };

  const handleSaveSplit = async () => {
    if (!selectedTxId) return;
    try {
      await client.put(`/api/transactions/${selectedTxId}`, {
        is_reimbursement: 1,
        self_amount: selfAmt,
        reimbursement_status: 'pending'
      });
      fetchData();
      setSelectedTxId('');
      setAiInput('');
      setSelfAmt(0);
    } catch (error) {
      console.error('Failed to save split', error);
    }
  };

  const handleComplete = async (id: string) => {
    try {
      await client.put(`/api/transactions/${id}`, {
        reimbursement_status: 'completed'
      });
      fetchData();
    } catch (error) {
      console.error('Failed to complete reimbursement', error);
    }
  };

  const selectedTx = recentTransactions.find(t => t.transaction_id === selectedTxId);

  return (
    <>
      <TopHeader title="立替・精算管理" onRefresh={fetchData} />
      
      <div className="page-content">
        {/* AI Detection Section */}
        <div className="card mb-4">
          <div className="card-header">
            <h3><Zap size={20} /> これ立替？ (AI Detection)</h3>
            <button className="btn-primary" onClick={handleDetect} disabled={detecting}>
              {detecting ? '解析中...' : 'AIに判定させる'}
            </button>
          </div>
          <div className="card-body">
            {suggestions.length > 0 ? (
              <div className="suggestions-list">
                {suggestions.map((sug) => {
                  const tx = recentTransactions.find(t => t.transaction_id === sug.transaction_id);
                  return tx ? (
                    <div key={tx.transaction_id} className="review-summary mb-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <strong>{tx.transaction_date} | {tx.comment || tx.category} | {tx.amount.toLocaleString()}円</strong>
                          <p className="mt-2 text-muted">🤖 {sug.reason}</p>
                        </div>
                        <div className="flex gap-2">
                          <button className="btn-success btn-small" onClick={() => handleApplySuggestion(tx.transaction_id)}>立替にする</button>
                          <button className="btn-text btn-small" onClick={() => setSuggestions(suggestions.filter(s => s.transaction_id !== tx.transaction_id))}>無視</button>
                        </div>
                      </div>
                    </div>
                  ) : null;
                })}
              </div>
            ) : (
              <div className="text-muted">「AIに判定させる」ボタンを押すと、最近の明細から立替の可能性があるものを探します。</div>
            )}
          </div>
        </div>

        <div className="dashboard-grid" style={{ padding: 0 }}>
          {/* Pending List */}
          <div className="card section-budget">
            <div className="card-header">
              <h3><Handshake size={20} /> 精算待ちリスト</h3>
            </div>
            <div className="card-body">
              {pending.length > 0 ? (
                <ul className="pending-list">
                  {pending.map((item) => (
                    <li key={item.transaction_id}>
                      <div className="pending-info">
                        <span className="date">{item.transaction_date}</span>
                        <span className="desc">{item.comment || item.category}</span>
                        <span className="text-muted" style={{ fontSize: '0.8rem' }}>
                          全体: {item.amount.toLocaleString()}円 / 自己負担: {item.self_amount?.toLocaleString()}円
                        </span>
                      </div>
                      <div className="flex flex-col items-end">
                        <div className="pending-amount">{item.pending_amount.toLocaleString()}円</div>
                        <button className="btn-outline btn-small mt-2" onClick={() => handleComplete(item.transaction_id)}>完了</button>
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-center py-4">
                  <CheckCircle2 size={48} className="text-success mb-2" style={{ opacity: 0.5 }} />
                  <p className="text-muted">未精算の項目はありません。</p>
                </div>
              )}
            </div>
          </div>

          {/* New Split Form */}
          <div className="card section-ai-review">
            <div className="card-header">
              <h3><Handshake size={20} /> 新しく立替を設定</h3>
            </div>
            <div className="card-body">
              <div className="form-group">
                <label>明細を選択</label>
                <select 
                  className="form-control" 
                  value={selectedTxId} 
                  onChange={(e) => setSelectedTxId(e.target.value)}
                >
                  <option value="">選択してください...</option>
                  {recentTransactions.map(tx => (
                    <option key={tx.transaction_id} value={tx.transaction_id}>
                      {tx.transaction_date} - {tx.comment || tx.category} ({tx.amount.toLocaleString()}円)
                    </option>
                  ))}
                </select>
              </div>

              {selectedTxId && (
                <>
                  <div className="form-group">
                    <label>AIで計算 (例: 4人で割り勘, 自分は5000円など)</label>
                    <div className="ai-input-group">
                      <input 
                        type="text" 
                        className="form-control" 
                        placeholder="入力してEnter..." 
                        value={aiInput}
                        onChange={(e) => setAiInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleAiParse()}
                      />
                      <button className="btn-outline" onClick={handleAiParse} disabled={parsing}>
                        {parsing ? '...' : '計算'}
                      </button>
                    </div>
                  </div>

                  <div className="form-group">
                    <label>自分の負担額 (円)</label>
                    <input 
                      type="number" 
                      className="form-control" 
                      value={selfAmt} 
                      onChange={(e) => setSelfAmt(parseInt(e.target.value))}
                    />
                  </div>

                  <div className="mt-4 p-3 bg-color rounded" style={{ backgroundColor: 'var(--bg-color)' }}>
                    <div className="flex justify-between mb-2">
                      <span className="text-muted">全体の金額:</span>
                      <span>{selectedTx?.amount.toLocaleString()} 円</span>
                    </div>
                    <div className="flex justify-between font-bold">
                      <span className="text-muted">相手の精算額:</span>
                      <span className="text-warning">{(selectedTx ? selectedTx.amount - selfAmt : 0).toLocaleString()} 円</span>
                    </div>
                  </div>

                  <button className="btn-primary w-100 mt-4" onClick={handleSaveSplit}>
                    立替として設定を保存
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default ExpenseSplitter;
