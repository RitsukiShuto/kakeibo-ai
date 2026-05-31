import React from 'react';
import { Wallet, Settings as SettingsIcon, AlertTriangle } from 'lucide-react';

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
    <div className="flex flex-col gap-6" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {isOverBudget && (
        <div className="review-summary" style={{ borderLeftColor: 'var(--danger)', backgroundColor: 'rgba(239, 68, 68, 0.1)', color: 'var(--text-main)' }}>
          <AlertTriangle size={18} className="text-danger inline mr-2" style={{ verticalAlign: 'text-bottom' }} />
          <span className="font-bold">警告: </span>
          予算・目標の合計（{totalBudgetAmount.toLocaleString()}円）が、月間総収入（{incomeAmount.toLocaleString()}円）を上回っています。このままでは赤字になる可能性があります。
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <h3><Wallet size={20} /> 全体目標</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
            <div className="form-group mb-0">
              <label>月間総収入</label>
              <input 
                type="number" className="form-control" 
                value={budget?.monthly?.income || 0} 
                onChange={(e) => updateBudgetField('monthly.income', parseInt(e.target.value))} 
              />
            </div>
            <div className="form-group mb-0">
              <label>貯蓄目標額</label>
              <input 
                type="number" className="form-control" 
                value={budget?.monthly?.savings_goal || 0} 
                onChange={(e) => updateBudgetField('monthly.savings_goal', parseInt(e.target.value))} 
              />
            </div>
            <div className="form-group mb-0">
              <label>投資目標額</label>
              <input 
                type="number" className="form-control" 
                value={budget?.monthly?.investment_goal || 0} 
                onChange={(e) => updateBudgetField('monthly.investment_goal', parseInt(e.target.value))} 
              />
            </div>
            <div className="form-group mb-0" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '8px', border: `1px solid ${surplus >= 0 ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}` }}>
              <label style={{ color: surplus >= 0 ? 'var(--success)' : 'var(--danger)' }}>割り振り可能な余剰資金</label>
              <div style={{ fontSize: '1.4rem', fontWeight: 'bold', color: surplus >= 0 ? 'var(--success)' : 'var(--danger)', marginTop: 'auto' }}>
                {surplus >= 0 ? '+' : ''}{surplus.toLocaleString()} 円
              </div>
            </div>
          </div>
        </div>
      </div>

      {['fixed', 'variable'].map((section) => (
        <div key={section} className="card">
          <div className="card-header">
            <h3><SettingsIcon size={20} /> カテゴリ別予算 ({section === 'fixed' ? '固定費' : '変動費'})</h3>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }}>
              {Object.entries(budget?.monthly?.budget?.[section] || {}).map(([category, subcategories]: [string, any]) => (
                <div key={category} className="budget-category-box" style={{ position: 'relative' }}>
                  <button 
                    onClick={() => handleDeleteCategory(section, category)}
                    style={{ position: 'absolute', top: '16px', right: '16px', background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '1.2rem', lineHeight: 1 }}
                    title="この項目を削除"
                  >×</button>
                  <div className="budget-category-title" style={{ paddingRight: '24px' }}>{category}</div>
                  {typeof subcategories === 'object' ? (
                    Object.entries(subcategories).map(([sub, amount]: [string, any]) => (
                      <div key={sub} className="form-group mb-2">
                        <label style={{ fontSize: '0.75rem' }}>{sub}</label>
                        <input 
                          type="number" className="form-control form-control-sm" 
                          value={amount} 
                          onChange={(e) => {
                            const newBudget = { ...budget };
                            newBudget.monthly.budget[section][category][sub] = parseInt(e.target.value) || 0;
                            setBudget(newBudget);
                            setBudgetJson(JSON.stringify(newBudget, null, 2));
                          }} 
                        />
                      </div>
                    ))
                  ) : (
                    <div className="form-group">
                      <input 
                        type="number" className="form-control form-control-sm" 
                        value={subcategories} 
                        onChange={(e) => {
                          const newBudget = { ...budget };
                          newBudget.monthly.budget[section][category] = parseInt(e.target.value) || 0;
                          setBudget(newBudget);
                          setBudgetJson(JSON.stringify(newBudget, null, 2));
                        }} 
                      />
                    </div>
                  )}
                </div>
              ))}
              
              <div 
                className="budget-category-box" 
                style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', borderStyle: 'dashed', cursor: 'pointer', background: 'transparent', opacity: 0.7, minHeight: '120px' }}
                onClick={() => handleAddCategory(section)}
              >
                <span style={{ color: 'var(--primary)', fontWeight: 'bold', fontSize: '1.1rem' }}>+ 新規項目を追加</span>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default BudgetSettings;
