import React, { useEffect, useState } from 'react';
import { Search, Save, X, Edit2, ChevronDown, ChevronUp, ArrowUp, Trash2, Plus } from 'lucide-react';
import client from '../api/client';
import type { Transaction, CategoryMetadata } from '../api/client';
import TopHeader from '../components/TopHeader';

const LIMIT = 50;

const Transactions: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [categories, setCategories] = useState<CategoryMetadata[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValues, setEditValues] = useState<Partial<Transaction>>({});
  const [isAdding, setIsAdding] = useState(false);
  const [newTransaction, setNewTransaction] = useState<Partial<Transaction>>({
    transaction_date: new Date().toISOString().split('T')[0],
    category: '',
    genre: '',
    amount: 0,
    comment: '',
    source: 'manual',
    mode: 'payment',
    is_reimbursement: 0
  });
  
  const [sortConfig, setSortConfig] = useState<{ key: keyof Transaction | null, direction: 'asc' | 'desc' }>({ key: null, direction: 'asc' });
  const [showTopBtn, setShowTopBtn] = useState(false);

  const fetchTransactions = async (currentOffset: number, append: boolean = false) => {
    if (append) {
      setLoadingMore(true);
    } else {
      setLoading(true);
    }
    
    try {
      const res = await client.get<Transaction[]>(`/api/transactions?limit=${LIMIT}&offset=${currentOffset}&search=${search}`);
      const newTransactions = res.data;
      
      if (append) {
        setTransactions(prev => [...prev, ...newTransactions]);
      } else {
        setTransactions(newTransactions);
      }
      
      setHasMore(newTransactions.length === LIMIT);
    } catch (error) {
      console.error('Failed to fetch transactions', error);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const res = await client.get<CategoryMetadata[]>('/api/transactions/categories');
      setCategories(res.data);
    } catch (error) {
      console.error('Failed to fetch categories', error);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      setOffset(0);
      fetchTransactions(0, false);
    }, 500);
    return () => clearTimeout(timer);
  }, [search]);

  useEffect(() => {
    const handleScroll = () => {
      setShowTopBtn(window.scrollY > 300);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleSort = (key: keyof Transaction) => {
    let direction: 'asc' | 'desc' = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const sortedTransactions = [...transactions].sort((a, b) => {
    if (!sortConfig.key) return 0;
    
    const valA = a[sortConfig.key] || '';
    const valB = b[sortConfig.key] || '';

    if (valA < valB) return sortConfig.direction === 'asc' ? -1 : 1;
    if (valA > valB) return sortConfig.direction === 'asc' ? 1 : -1;
    return 0;
  });

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleLoadMore = () => {
    const nextOffset = offset + LIMIT;
    setOffset(nextOffset);
    fetchTransactions(nextOffset, true);
  };

  const handleEdit = (tx: Transaction) => {
    setEditingId(tx.transaction_id);
    setEditValues({
      category: tx.category,
      genre: tx.genre,
      comment: tx.comment,
      is_reimbursement: tx.is_reimbursement,
      self_amount: tx.self_amount
    });
  };

  const handleSave = async (id: string) => {
    try {
      await client.put(`/api/transactions/${id}`, editValues);
      setEditingId(null);
      // Reload current data without resetting offset (just simple refresh for now)
      fetchTransactions(0, false);
      setOffset(0);
    } catch (error) {
      console.error('Failed to update transaction', error);
    }
  };

  const handleCancel = () => {
    setEditingId(null);
    setEditValues({});
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('この明細を削除してもよろしいですか？')) return;
    try {
      await client.delete(`/api/transactions/${id}`);
      setTransactions(prev => prev.filter(t => t.transaction_id !== id));
    } catch (error) {
      console.error('Failed to delete transaction', error);
    }
  };

  const handleAdd = async () => {
    if (!newTransaction.category || !newTransaction.amount) {
      alert('カテゴリと金額を入力してください');
      return;
    }
    try {
      await client.post('/api/transactions', newTransaction);
      setIsAdding(false);
      setNewTransaction({
        transaction_date: new Date().toISOString().split('T')[0],
        category: '',
        genre: '',
        amount: 0,
        comment: '',
        source: 'manual',
        mode: 'payment',
        is_reimbursement: 0
      });
      fetchTransactions(0, false);
      setOffset(0);
    } catch (error) {
      console.error('Failed to create transaction', error);
    }
  };

  // ユニークな大項目を取得
  const majorCategories = Array.from(new Set(categories.map(c => c.category))).sort();
  // 選択された大項目に属する中項目を取得
  const getGenres = (category?: string) => categories
    .filter(c => c.category === category)
    .map(c => c.genre)
    .filter(g => g !== '')
    .sort();

  return (
    <>
      <TopHeader title="明細一覧" onRefresh={() => { setOffset(0); fetchTransactions(0, false); }} />
      
      <div className="page-content">
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
          <div className="card" style={{ flex: 1, marginBottom: 0 }}>
            <div className="card-body">
              <div className="ai-input-group">
                <Search size={20} className="text-muted" style={{ alignSelf: 'center', marginLeft: '12px' }} />
                <input 
                  type="text" 
                  className="form-control" 
                  placeholder="明細を検索 (内容、カテゴリ、金額など)..." 
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>
            </div>
          </div>
          <button className="btn-primary" onClick={() => setIsAdding(!isAdding)} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Plus size={20} /> 新規作成
          </button>
        </div>

        {isAdding && (
          <div className="card mb-6" style={{ border: '1px solid var(--primary)', background: 'rgba(59, 130, 246, 0.05)' }}>
            <div className="card-header">
              <h3>新しい明細の入力</h3>
            </div>
            <div className="card-body">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                <div className="form-group">
                  <label>日付</label>
                  <input type="date" className="form-control" value={newTransaction.transaction_date} onChange={e => setNewTransaction({...newTransaction, transaction_date: e.target.value})} />
                </div>
                <div className="form-group">
                  <label>区分</label>
                  <select className="form-control" value={newTransaction.mode} onChange={e => setNewTransaction({...newTransaction, mode: e.target.value})}>
                    <option value="payment">支出</option>
                    <option value="income">収入</option>
                    <option value="transfer">振替</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>金額</label>
                  <input type="number" className="form-control" value={newTransaction.amount || ''} onChange={e => setNewTransaction({...newTransaction, amount: parseInt(e.target.value) || 0})} />
                </div>
                <div className="form-group">
                  <label>大項目</label>
                  <select className="form-control" value={newTransaction.category} onChange={e => setNewTransaction({...newTransaction, category: e.target.value, genre: ''})}>
                    <option value="">選択してください</option>
                    {majorCategories.map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>中項目</label>
                  <select className="form-control" value={newTransaction.genre} onChange={e => setNewTransaction({...newTransaction, genre: e.target.value})} disabled={!newTransaction.category}>
                    <option value="">未分類</option>
                    {getGenres(newTransaction.category).map(g => <option key={g} value={g}>{g}</option>)}
                  </select>
                </div>
                <div className="form-group" style={{ gridColumn: 'span 2' }}>
                  <label>内容</label>
                  <input type="text" className="form-control" value={newTransaction.comment} onChange={e => setNewTransaction({...newTransaction, comment: e.target.value})} />
                </div>
                <div className="form-group" style={{ display: 'flex', alignItems: 'flex-end', gap: '12px' }}>
                  <button className="btn-primary" style={{ flex: 1 }} onClick={handleAdd}>追加する</button>
                  <button className="btn-outline" onClick={() => setIsAdding(false)}>閉じる</button>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="card">
          <div className="card-body" style={{ overflowX: 'auto', padding: 0 }}>
            <table className="transaction-table">
              <thead>
                <tr>
                  <th style={{ width: '120px', cursor: 'pointer' }} onClick={() => handleSort('transaction_date')}>
                    日付 {sortConfig.key === 'transaction_date' ? (sortConfig.direction === 'asc' ? <ChevronUp size={14} className="inline" /> : <ChevronDown size={14} className="inline" />) : null}
                  </th>
                  <th style={{ width: '150px', cursor: 'pointer' }} onClick={() => handleSort('category')}>
                    大項目 {sortConfig.key === 'category' ? (sortConfig.direction === 'asc' ? <ChevronUp size={14} className="inline" /> : <ChevronDown size={14} className="inline" />) : null}
                  </th>
                  <th style={{ width: '150px', cursor: 'pointer' }} onClick={() => handleSort('genre')}>
                    中項目 {sortConfig.key === 'genre' ? (sortConfig.direction === 'asc' ? <ChevronUp size={14} className="inline" /> : <ChevronDown size={14} className="inline" />) : null}
                  </th>
                  <th style={{ width: '120px', cursor: 'pointer' }} onClick={() => handleSort('amount')}>
                    金額 {sortConfig.key === 'amount' ? (sortConfig.direction === 'asc' ? <ChevronUp size={14} className="inline" /> : <ChevronDown size={14} className="inline" />) : null}
                  </th>
                  <th style={{ cursor: 'pointer' }} onClick={() => handleSort('comment')}>
                    内容 {sortConfig.key === 'comment' ? (sortConfig.direction === 'asc' ? <ChevronUp size={14} className="inline" /> : <ChevronDown size={14} className="inline" />) : null}
                  </th>
                  <th style={{ width: '100px', cursor: 'pointer' }} onClick={() => handleSort('is_reimbursement')}>
                    立替 {sortConfig.key === 'is_reimbursement' ? (sortConfig.direction === 'asc' ? <ChevronUp size={14} className="inline" /> : <ChevronDown size={14} className="inline" />) : null}
                  </th>
                  <th style={{ width: '100px' }}>操作</th>
                </tr>
              </thead>
              <tbody>
                {sortedTransactions.map((tx) => (
                  <tr key={tx.transaction_id} className={editingId === tx.transaction_id ? 'editing-row' : ''}>
                    <td style={{ fontSize: '0.85rem' }}>{tx.transaction_date}</td>
                    <td>
                      {editingId === tx.transaction_id ? (
                        <select 
                          className="form-control form-control-sm"
                          value={editValues.category || ''}
                          onChange={(e) => setEditValues({ ...editValues, category: e.target.value, genre: '' })}
                        >
                          <option value="">選択してください</option>
                          {majorCategories.map(c => <option key={c} value={c}>{c}</option>)}
                        </select>
                      ) : (
                        <span className="badge-category">{tx.category}</span>
                      )}
                    </td>
                    <td>
                      {editingId === tx.transaction_id ? (
                        <select 
                          className="form-control form-control-sm"
                          value={editValues.genre || ''}
                          onChange={(e) => setEditValues({ ...editValues, genre: e.target.value })}
                          disabled={!editValues.category}
                        >
                          <option value="">未分類</option>
                          {getGenres(editValues.category).map(g => <option key={g} value={g}>{g}</option>)}
                          {!getGenres(editValues.category).includes(tx.genre) && tx.genre && <option value={tx.genre}>{tx.genre}</option>}
                        </select>
                      ) : (
                        <span className="text-muted" style={{ fontSize: '0.9rem' }}>{tx.genre || '-'}</span>
                      )}
                    </td>
                    <td style={{ fontWeight: '600', color: tx.mode === 'income' ? 'var(--success)' : 'inherit' }}>
                      {tx.amount.toLocaleString()}円
                    </td>
                    <td>
                      {editingId === tx.transaction_id ? (
                        <input 
                          type="text" 
                          className="form-control form-control-sm" 
                          value={editValues.comment || ''} 
                          onChange={(e) => setEditValues({ ...editValues, comment: e.target.value })}
                        />
                      ) : (
                        <div className="text-truncate" style={{ maxWidth: '300px' }} title={tx.comment}>
                          {tx.comment || '-'}
                        </div>
                      )}
                    </td>
                    <td>
                      {editingId === tx.transaction_id ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                          <label style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', cursor: 'pointer' }}>
                            <input 
                              type="checkbox" 
                              checked={!!editValues.is_reimbursement} 
                              onChange={(e) => setEditValues({ ...editValues, is_reimbursement: e.target.checked ? 1 : 0 })}
                            />
                            立替
                          </label>
                          {editValues.is_reimbursement ? (
                            <input 
                              type="number" 
                              className="form-control form-control-sm" 
                              style={{ width: '80px' }}
                              value={editValues.self_amount || 0} 
                              onChange={(e) => setEditValues({ ...editValues, self_amount: parseInt(e.target.value) })}
                              placeholder="負担額"
                            />
                          ) : null}
                        </div>
                      ) : (
                        tx.is_reimbursement ? <span className="badge badge-split">立替</span> : '-'
                      )}
                    </td>
                    <td>
                      {editingId === tx.transaction_id ? (
                        <div style={{ display: 'flex', gap: '4px' }}>
                          <button className="btn-success btn-small" onClick={() => handleSave(tx.transaction_id)} title="保存">
                            <Save size={14} />
                          </button>
                          <button className="btn-text btn-small" onClick={handleCancel} title="キャンセル">
                            <X size={14} />
                          </button>
                        </div>
                      ) : (
                        <div style={{ display: 'flex', gap: '4px' }}>
                          <button className="btn-outline btn-small" onClick={() => handleEdit(tx)} title="編集">
                            <Edit2 size={14} />
                          </button>
                          <button className="btn-text btn-small text-danger" onClick={() => handleDelete(tx.transaction_id)} title="削除">
                            <Trash2 size={14} />
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {transactions.length === 0 && !loading && (
              <div className="text-muted p-8 text-center" style={{ padding: '32px' }}>明細が見つかりません。</div>
            )}
            
            {loading && !loadingMore && <div className="text-center text-muted" style={{ padding: '32px' }}>読み込み中...</div>}
            
            {hasMore && transactions.length > 0 && (
              <div style={{ padding: '24px', textAlign: 'center', borderTop: '1px solid var(--border)' }}>
                <button 
                  className="btn-outline" 
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}
                  onClick={handleLoadMore}
                  disabled={loadingMore}
                >
                  {loadingMore ? '読み込み中...' : 'さらに読み込む'} 
                  {!loadingMore && <ChevronDown size={16} />}
                </button>
              </div>
            )}
            
          </div>
        </div>
      </div>
      
      {showTopBtn && (
        <button 
          onClick={scrollToTop}
          className="btn-primary"
          style={{
            position: 'fixed',
            bottom: '40px',
            right: '40px',
            zIndex: 1000,
            borderRadius: '50%',
            width: '48px',
            height: '48px',
            padding: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
            animation: 'fadeIn 0.3s ease-out'
          }}
          title="トップへ戻る"
        >
          <ArrowUp size={24} />
        </button>
      )}

      <style>{`
        .badge-category {
          background: rgba(59, 130, 246, 0.1);
          color: var(--primary);
          padding: 4px 10px;
          border-radius: 6px;
          font-size: 0.85rem;
          font-weight: 500;
        }
        .editing-row {
          background-color: rgba(59, 130, 246, 0.05);
        }
        .form-control-sm {
          padding: 6px 10px;
          font-size: 0.85rem;
          height: auto;
          background: rgba(0,0,0,0.4);
        }
        .btn-small {
          padding: 4px 8px;
        }
        .mb-6 {
          margin-bottom: 1.5rem;
        }
      `}</style>
    </>
  );
};

export default Transactions;
