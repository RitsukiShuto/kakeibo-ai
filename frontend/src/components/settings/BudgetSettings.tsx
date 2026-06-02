import React from 'react';
import { Wallet, Settings as SettingsIcon, AlertTriangle, Plus, Trash2 } from 'lucide-react';

interface BudgetSettingsProps {
  budget: any;
  updateBudgetField: (path: string, value: any) => void;
  handleAddCategory: (section: string) => void;
  handleDeleteCategory: (section: string, category: string) => void;
  setBudget: (budget: any) => void;
  setBudgetJson: (json: string) => void;
}

const BudgetSettings: React.FC<BudgetSettingsProps> = ({ 
  budget, updateBudgetField, handleAddCategory, handleDeleteCategory, setBudget, setBudgetJson 
}) => {
  const incomeAmount = budget?.monthly?.income || 0;
  let totalBudgetAmount = 0;
  totalBudgetAmount += budget?.monthly?.savings_goal || 0;
  totalBudgetAmount += budget?.monthly?.investment_goal || 0;
  
  const calcSection = (sectionData: any) => {
    if (!sectionData) return;
    Object.values(sectionData).forEach((val: any) => {
      if (typeof val === 'number') totalBudgetAmount += val;
      else if (typeof val === 'object' && val !== null) {
        Object.values(val).forEach((v: any) => {
          if (typeof v === 'number') totalBudgetAmount += v;
        });
      }
    });
  };
  calcSection(budget?.monthly?.budget?.fixed);
  calcSection(budget?.monthly?.budget?.variable);
  
  const isOverBudget = incomeAmount > 0 && totalBudgetAmount > incomeAmount;
  const surplus = incomeAmount - totalBudgetAmount;

  return (
    <div className="flex flex-col gap-8" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {isOverBudget && (
        <div className="review-summary animate-pulse-slow" style={{ borderLeftColor: 'var(--danger)', backgroundColor: 'rgba(239, 68, 68, 0.05)', color: 'var(--text-main)' }}>
          <AlertTriangle size={20} className="text-danger inline mr-3" style={{ verticalAlign: 'middle' }} />
          <span className="font-bold">警告: </span>
          予算・目標の合計（{totalBudgetAmount.toLocaleString()}円）が、月間総収入（{incomeAmount.toLocaleString()}円）を上回っています。
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <h3><Wallet size={20} /> 全体収支目標</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.5rem' }}>
            <div className="form-group mb-0">
              <label>月間総収入</label>
              <div style={{ position: 'relative' }}>
                <input 
                  type="number" className="form-control" 
                  value={budget?.monthly?.income || 0} 
                  onChange={(e) => updateBudgetField('monthly.income', parseInt(e.target.value) || 0)} 
                />
                <span style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', opacity: 0.5, fontSize: '0.8rem' }}>円</span>
              </div>
            </div>
            <div className="form-group mb-0">
              <label>貯蓄目標</label>
              <div style={{ position: 'relative' }}>
                <input 
                  type="number" className="form-control" 
                  value={budget?.monthly?.savings_goal || 0} 
                  onChange={(e) => updateBudgetField('monthly.savings_goal', parseInt(e.target.value) || 0)} 
                />
                <span style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', opacity: 0.5, fontSize: '0.8rem' }}>円</span>
              </div>
            </div>
            <div className="form-group mb-0">
              <label>投資目標</label>
              <div style={{ position: 'relative' }}>
                <input 
                  type="number" className="form-control" 
                  value={budget?.monthly?.investment_goal || 0} 
                  onChange={(e) => updateBudgetField('monthly.investment_goal', parseInt(e.target.value) || 0)} 
                />
                <span style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', opacity: 0.5, fontSize: '0.8rem' }}>円</span>
              </div>
            </div>
            <div className="form-group mb-0 glass" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '12px 16px', borderRadius: '12px', border: `1px solid ${surplus >= 0 ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'}` }}>
              <label style={{ color: surplus >= 0 ? 'var(--success)' : 'var(--danger)', fontSize: '0.75rem', marginBottom: '4px' }}>余剰 / 不足</label>
              <div style={{ fontSize: '1.25rem', fontWeight: '900', color: surplus >= 0 ? 'var(--success)' : 'var(--danger)' }}>
                {surplus >= 0 ? '+' : ''}{surplus.toLocaleString()} <span style={{ fontSize: '0.9rem' }}>円</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {['fixed', 'variable'].map((section) => (
        <div key={section} className="card">
          <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3><SettingsIcon size={20} /> {section === 'fixed' ? '固定費 (Fixed)' : '変動費 (Variable)'}</h3>
            <button className="btn-text btn-small" onClick={() => handleAddCategory(section)}>
              <Plus size={16} /> 追加
            </button>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }}>
              {Object.entries(budget?.monthly?.budget?.[section] || {}).map(([category, subcategories]: [string, any]) => (
                <div key={category} className="budget-category-box glass" style={{ position: 'relative', border: '1px solid var(--border)', borderRadius: '16px', padding: '1.25rem' }}>
                  <button 
                    onClick={() => handleDeleteCategory(section, category)}
                    style={{ position: 'absolute', top: '12px', right: '12px', background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', opacity: 0.4 }}
                    className="hover:opacity-100 transition-opacity"
                  ><Trash2 size={16} /></button>
                  
                  <div className="budget-category-title" style={{ fontSize: '1rem', fontWeight: '800', marginBottom: '1.25rem', color: section === 'fixed' ? 'var(--warning)' : 'var(--success)' }}>
                    {category}
                  </div>
                  
                  {typeof subcategories === 'object' ? (
                    <div className="space-y-4" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                      {Object.entries(subcategories).map(([sub, amount]: [string, any]) => (
                        <div key={sub} className="form-group mb-0">
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                            <label style={{ fontSize: '0.8rem', opacity: 0.7, marginBottom: 0 }}>{sub}</label>
                          </div>
                          <div style={{ position: 'relative' }}>
                            <input 
                              type="number" className="form-control form-control-sm" 
                              value={amount} 
                              onChange={(e) => {
                                const newBudget = { ...budget };
                                newBudget.monthly.budget[section][category][sub] = parseInt(e.target.value) || 0;
                                setBudget(newBudget);
                                setBudgetJson(JSON.stringify(newBudget, null, 2));
                              }} 
                              style={{ paddingRight: '32px' }}
                            />
                            <span style={{ position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)', opacity: 0.3, fontSize: '0.7rem' }}>円</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="form-group mb-0">
                      <div style={{ position: 'relative' }}>
                        <input 
                          type="number" className="form-control" 
                          value={subcategories} 
                          onChange={(e) => {
                            const newBudget = { ...budget };
                            newBudget.monthly.budget[section][category] = parseInt(e.target.value) || 0;
                            setBudget(newBudget);
                            setBudgetJson(JSON.stringify(newBudget, null, 2));
                          }} 
                          style={{ paddingRight: '32px' }}
                        />
                        <span style={{ position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)', opacity: 0.3, fontSize: '0.7rem' }}>円</span>
                      </div>
                    </div>
                  )}
                </div>
              ))}
              
              <div 
                className="budget-category-box glass" 
                style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', borderStyle: 'dashed', cursor: 'pointer', background: 'transparent', opacity: 0.5, minHeight: '140px', borderRadius: '16px' }}
                onClick={() => handleAddCategory(section)}
              >
                <div style={{ textAlign: 'center' }}>
                  <Plus size={32} style={{ margin: '0 auto 8px', color: 'var(--primary)' }} />
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>項目を追加</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default BudgetSettings;
