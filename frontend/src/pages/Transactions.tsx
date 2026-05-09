import React, { useEffect, useState } from 'react';
import { Search, Save } from 'lucide-react';
import client from '../api/client';
import type { Transaction } from '../api/client';
import TopHeader from '../components/TopHeader';

const Transactions: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValues, setEditValues] = useState<Partial<Transaction>>({});

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      const res = await client.get<Transaction[]>(`/api/transactions?limit=100&search=${search}`);
      setTransactions(res.data);
    } catch (error) {
      console.error('Failed to fetch transactions', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchTransactions();
    }, 500);
    return () => clearTimeout(timer);
  }, [search]);

  const handleEdit = (tx: Transaction) => {
    setEditingId(tx.transaction_id);
    setEditValues({
      category: tx.category,
      comment: tx.comment,
      is_reimbursement: tx.is_reimbursement,
      self_amount: tx.self_amount
    });
  };

  const handleSave = async (id: string) => {
    try {
      await client.put(`/api/transactions/${id}`, editValues);
      setEditingId(null);
      fetchTransactions();
    } catch (error) {
      console.error('Failed to update transaction', error);
    }
  };

  const handleCancel = () => {
    setEditingId(null);
    setEditValues({});
  };

  return (
    <>
      <TopHeader title="明細一覧" onRefresh={fetchTransactions} />
      
      <div className="page-content">
        <div className="card mb-4">
          <div className="card-body">
            <div className="ai-input-group">
              <Search size={20} className="text-muted" style={{ alignSelf: 'center' }} />
              <input 
                type="text" 
                className="form-control" 
                placeholder="明細を検索 (摘要やカテゴリ)..." 
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body" style={{ overflowX: 'auto' }}>
            <table className="transaction-table">
              <thead>
                <tr>
                  <th>日付</th>
                  <th>カテゴリ</th>
                  <th>金額</th>
                  <th>内容</th>
                  <th>立替</th>
                  <th>アクション</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((tx) => (
                  <tr key={tx.transaction_id}>
                    <td>{tx.transaction_date}</td>
                    <td>
                      {editingId === tx.transaction_id ? (
                        <input 
                          type="text" 
                          className="form-control" 
                          value={editValues.category || ''} 
                          onChange={(e) => setEditValues({ ...editValues, category: e.target.value })}
                        />
                      ) : (
                        tx.category
                      )}
                    </td>
                    <td>{tx.amount.toLocaleString()}円</td>
                    <td>
                      {editingId === tx.transaction_id ? (
                        <input 
                          type="text" 
                          className="form-control" 
                          value={editValues.comment || ''} 
                          onChange={(e) => setEditValues({ ...editValues, comment: e.target.value })}
                        />
                      ) : (
                        tx.comment || '-'
                      )}
                    </td>
                    <td>
                      {editingId === tx.transaction_id ? (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <input 
                            type="checkbox" 
                            checked={!!editValues.is_reimbursement} 
                            onChange={(e) => setEditValues({ ...editValues, is_reimbursement: e.target.checked ? 1 : 0 })}
                          />
                          {editValues.is_reimbursement ? (
                            <input 
                              type="number" 
                              className="form-control" 
                              style={{ width: '80px' }}
                              value={editValues.self_amount || 0} 
                              onChange={(e) => setEditValues({ ...editValues, self_amount: parseInt(e.target.value) })}
                            />
                          ) : null}
                        </div>
                      ) : (
                        tx.is_reimbursement ? <span className="badge badge-split">立替</span> : '-'
                      )}
                    </td>
                    <td>
                      {editingId === tx.transaction_id ? (
                        <div style={{ display: 'flex', gap: '8px' }}>
                          <button className="btn-success btn-small" onClick={() => handleSave(tx.transaction_id)}>
                            <Save size={14} />
                          </button>
                          <button className="btn-text btn-small" onClick={handleCancel}>キャンセル</button>
                        </div>
                      ) : (
                        <button className="btn-outline btn-small" onClick={() => handleEdit(tx)}>編集</button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {transactions.length === 0 && !loading && (
              <div className="text-muted mt-4 text-center">明細が見つかりません。</div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default Transactions;
