import React, { useEffect, useState } from 'react';
import { Search, Save, X, Edit2, ChevronDown, ChevronUp, Trash2, Plus, Download, Filter } from 'lucide-react';
import client from '../api/client';
import type { Transaction, CategoryMetadata } from '../api/client';

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

  const majorCategories = Array.from(new Set(categories.map(c => c.category))).sort();
  const getGenres = (category?: string) => categories
    .filter(c => c.category === category)
    .map(c => c.genre)
    .filter(g => g !== '')
    .sort();

  const getCategoryColor = (category: string) => {
    const hash = Array.from(category).reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const colors = [
      'bg-indigo-500/20 text-indigo-400 border-indigo-500/30',
      'bg-rose-500/20 text-rose-400 border-rose-500/30',
      'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
      'bg-amber-500/20 text-amber-400 border-amber-500/30',
      'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
      'bg-purple-500/20 text-purple-400 border-purple-500/30',
      'bg-fuchsia-500/20 text-fuchsia-400 border-fuchsia-500/30',
    ];
    return colors[hash % colors.length];
  };

  return (
    <div className="max-w-[1100px] mx-auto px-8 py-12 min-h-screen text-slate-100">
      <header className="flex justify-between items-center mb-10 pb-6 border-b border-slate-800">
        <div className="text-2xl font-black tracking-tighter text-indigo-400">Transactions</div>
        <div className="flex gap-4">
          <div className="relative">
            <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input 
              type="text" 
              className="bg-slate-900 border border-slate-800 rounded-full pl-10 pr-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors w-64"
              placeholder="明細を検索..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-full text-sm font-bold flex items-center gap-2 transition-colors" onClick={() => setIsAdding(!isAdding)}>
            <Plus size={16} /> 新規作成
          </button>
        </div>
      </header>

      {isAdding && (
        <div className="bg-slate-900/50 p-6 rounded-3xl border border-slate-800 mb-8">
          <h3 className="text-lg font-bold text-slate-300 mb-6">新しい明細の入力</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">日付</label>
              <input type="date" className="bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500" value={newTransaction.transaction_date} onChange={e => setNewTransaction({...newTransaction, transaction_date: e.target.value})} />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">区分</label>
              <select className="bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500" value={newTransaction.mode} onChange={e => setNewTransaction({...newTransaction, mode: e.target.value})}>
                <option value="payment">支出</option>
                <option value="income">収入</option>
                <option value="transfer">振替</option>
              </select>
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">金額</label>
              <input type="number" className="bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500" value={newTransaction.amount || ''} onChange={e => setNewTransaction({...newTransaction, amount: parseInt(e.target.value) || 0})} />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">大項目</label>
              <select className="bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500" value={newTransaction.category} onChange={e => setNewTransaction({...newTransaction, category: e.target.value, genre: ''})}>
                <option value="">選択してください</option>
                {majorCategories.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">中項目</label>
              <select className="bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500" value={newTransaction.genre} onChange={e => setNewTransaction({...newTransaction, genre: e.target.value})} disabled={!newTransaction.category}>
                <option value="">未分類</option>
                {getGenres(newTransaction.category).map(g => <option key={g} value={g}>{g}</option>)}
              </select>
            </div>
            <div className="flex flex-col gap-2 md:col-span-2">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">内容</label>
              <input type="text" className="bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500" value={newTransaction.comment} onChange={e => setNewTransaction({...newTransaction, comment: e.target.value})} />
            </div>
            <div className="flex items-end gap-3">
              <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-xl text-sm font-bold flex-1 transition-colors" onClick={handleAdd}>追加</button>
              <button className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2 rounded-xl text-sm font-bold transition-colors" onClick={() => setIsAdding(false)}>取消</button>
            </div>
          </div>
        </div>
      )}

      <div className="bg-slate-900/50 rounded-3xl border border-slate-800 overflow-hidden">
        <div className="flex justify-between items-center p-6 border-b border-slate-800">
          <h2 className="text-lg font-black flex items-center gap-4 text-slate-500 uppercase tracking-widest">
            History
          </h2>
          <div className="flex gap-2">
            <button className="text-slate-400 hover:text-slate-200 text-sm font-bold flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-slate-800 transition-colors">
              <Filter size={16} /> フィルタ
            </button>
            <button className="text-slate-400 hover:text-slate-200 text-sm font-bold flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-slate-800 transition-colors">
              <Download size={16} /> CSV
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/80 text-xs font-bold text-slate-500 uppercase tracking-widest">
                <th className="p-4 cursor-pointer hover:text-slate-300 w-[120px]" onClick={() => handleSort('transaction_date')}>
                  <div className="flex items-center gap-1">日付 {sortConfig.key === 'transaction_date' && (sortConfig.direction === 'asc' ? <ChevronUp size={14}/> : <ChevronDown size={14}/>)}</div>
                </th>
                <th className="p-4 cursor-pointer hover:text-slate-300 w-[150px]" onClick={() => handleSort('category')}>
                  <div className="flex items-center gap-1">カテゴリ {sortConfig.key === 'category' && (sortConfig.direction === 'asc' ? <ChevronUp size={14}/> : <ChevronDown size={14}/>)}</div>
                </th>
                <th className="p-4 cursor-pointer hover:text-slate-300" onClick={() => handleSort('comment')}>
                  <div className="flex items-center gap-1">摘要 {sortConfig.key === 'comment' && (sortConfig.direction === 'asc' ? <ChevronUp size={14}/> : <ChevronDown size={14}/>)}</div>
                </th>
                <th className="p-4 cursor-pointer hover:text-slate-300 text-right" onClick={() => handleSort('amount')}>
                  <div className="flex items-center justify-end gap-1">金額 {sortConfig.key === 'amount' && (sortConfig.direction === 'asc' ? <ChevronUp size={14}/> : <ChevronDown size={14}/>)}</div>
                </th>
                <th className="p-4 text-center w-[120px]">立替</th>
                <th className="p-4 text-right w-[100px]">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {sortedTransactions.map((tx) => (
                <tr key={tx.transaction_id} className={`hover:bg-slate-800/30 transition-colors ${editingId === tx.transaction_id ? 'bg-slate-800/50' : ''}`}>
                  <td className="p-4 text-sm text-slate-400 font-medium">
                    {tx.transaction_date.replace(/-/g, '/')}
                  </td>
                  <td className="p-4">
                    {editingId === tx.transaction_id ? (
                      <select className="bg-slate-900 border border-slate-700 rounded-lg px-2 py-1 text-sm text-slate-200 w-full" value={editValues.category || ''} onChange={(e) => setEditValues({ ...editValues, category: e.target.value, genre: '' })}>
                        <option value="">選択</option>
                        {majorCategories.map(c => <option key={c} value={c}>{c}</option>)}
                      </select>
                    ) : (
                      <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold border ${getCategoryColor(tx.category)}`}>
                        {tx.category}
                      </span>
                    )}
                  </td>
                  <td className="p-4">
                    {editingId === tx.transaction_id ? (
                      <input type="text" className="bg-slate-900 border border-slate-700 rounded-lg px-2 py-1 text-sm text-slate-200 w-full" value={editValues.comment || ''} onChange={(e) => setEditValues({ ...editValues, comment: e.target.value })}/>
                    ) : (
                      <div>
                        <div className="font-bold text-slate-200 text-sm truncate max-w-[200px] md:max-w-[300px]" title={tx.comment}>{tx.comment || '-'}</div>
                        {tx.genre && <div className="text-xs text-slate-500 mt-1">{tx.genre}</div>}
                      </div>
                    )}
                  </td>
                  <td className="p-4 text-right">
                    <div className={`text-xl font-black tracking-tight ${tx.mode === 'income' ? 'text-emerald-400' : 'text-slate-100'}`}>
                      {tx.mode === 'income' ? '+' : ''}¥{tx.amount.toLocaleString()}
                    </div>
                  </td>
                  <td className="p-4 text-center">
                    {editingId === tx.transaction_id ? (
                      <div className="flex flex-col items-center gap-2">
                        <label className="flex items-center gap-2 text-xs text-slate-400 cursor-pointer">
                          <input type="checkbox" className="rounded bg-slate-900 border-slate-700" checked={!!editValues.is_reimbursement} onChange={(e) => setEditValues({ ...editValues, is_reimbursement: e.target.checked ? 1 : 0 })}/>
                          立替
                        </label>
                        {editValues.is_reimbursement ? (
                          <input type="number" className="bg-slate-900 border border-slate-700 rounded-lg px-2 py-1 text-xs text-slate-200 w-[80px]" value={editValues.self_amount || 0} onChange={(e) => setEditValues({ ...editValues, self_amount: parseInt(e.target.value) })} placeholder="負担額"/>
                        ) : null}
                      </div>
                    ) : (
                      tx.is_reimbursement ? <span className="inline-block px-2 py-1 bg-amber-500/20 text-amber-500 border border-amber-500/30 rounded text-xs font-bold">立替</span> : <span className="text-slate-600">-</span>
                    )}
                  </td>
                  <td className="p-4 text-right">
                    {editingId === tx.transaction_id ? (
                      <div className="flex justify-end gap-2">
                        <button className="p-1.5 text-emerald-400 hover:bg-emerald-400/10 rounded transition-colors" onClick={() => handleSave(tx.transaction_id)} title="保存"><Save size={16} /></button>
                        <button className="p-1.5 text-slate-400 hover:bg-slate-800 rounded transition-colors" onClick={handleCancel} title="キャンセル"><X size={16} /></button>
                      </div>
                    ) : (
                      <div className="flex justify-end gap-2">
                        <button className="p-1.5 text-slate-400 hover:text-indigo-400 hover:bg-indigo-400/10 rounded transition-colors" onClick={() => handleEdit(tx)} title="編集"><Edit2 size={16} /></button>
                        <button className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-400/10 rounded transition-colors" onClick={() => handleDelete(tx.transaction_id)} title="削除"><Trash2 size={16} /></button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {transactions.length === 0 && !loading && (
            <div className="text-center p-12 text-slate-500 font-medium">明細が見つかりません。</div>
          )}
          {loading && !loadingMore && (
            <div className="text-center p-12 text-slate-500 font-medium animate-pulse">読み込み中...</div>
          )}
        </div>
        
        {hasMore && transactions.length > 0 && (
          <div className="p-4 border-t border-slate-800 text-center">
            <button className="text-sm font-bold text-indigo-400 hover:text-indigo-300 transition-colors flex items-center justify-center gap-2 mx-auto" onClick={handleLoadMore} disabled={loadingMore}>
              {loadingMore ? '読み込み中...' : 'さらに読み込む'} {!loadingMore && <ChevronDown size={16} />}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Transactions;
