# ダッシュボード全面刷新 実装プラン

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ダッシュボードをカードレイアウトから脱却し、"Vibrant Minimalist" デザインへと刷新する。日割り予算（ペースメーカー）や5段階タイムフレーム切替、資産チャートの統合を含む。

**Architecture:** Tailwind CSS を活用したフラットなコンポーネント設計。React の `useMemo` を用いて、選択されたタイムフレームに応じた動的な予実計算とペースメーカー位置の算出を行う。既存の `KakeiboAnalyzer` (Backend) から取得した統計データをフロントエンドで加工・表示する。

**Tech Stack:** React, TypeScript, Tailwind CSS, Lucide React, Recharts

---

### Task 1: ProgressBar コンポーネントの機能強化

**Files:**
- Modify: `frontend/src/components/ProgressBar.tsx`
- Modify: `frontend/src/components/__tests__/ProgressBar.test.tsx`

- [ ] **Step 1: テストケースの追加 (ペースメーカーと差分表示)**

```typescript
// frontend/src/components/__tests__/ProgressBar.test.tsx に追記
it('renders pace marker and difference when provided', () => {
  render(<ProgressBar label="Food" actual={18000} budget={30000} paceLimit={15000} showDiff={true} />);
  expect(screen.getByText('(-¥3,000)')).toBeInTheDocument(); // 超過分 18000 - 15000 = 3000
  const marker = document.querySelector('.pace-marker');
  expect(marker).toBeInTheDocument();
});
```

- [ ] **Step 2: テストの実行と失敗の確認**

Run: `cd frontend && npm test -- --run`
Expected: FAIL (Props `paceLimit`, `showDiff` が未定義)

- [ ] **Step 3: コンポーネントの改修**

```typescript
import React from 'react';

interface ProgressBarProps {
  label: string;
  actual: number;
  budget: number;
  paceLimit?: number; // 今日の理想ライン
  showDiff?: boolean;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ label, actual, budget, paceLimit, showDiff }) => {
  const percentage = budget > 0 ? Math.min((actual / budget) * 100, 100) : 0;
  const pacePercentage = (paceLimit && budget > 0) ? (paceLimit / budget) * 100 : null;
  
  // ペースとの乖離 (負が節約、正が超過)
  const diff = paceLimit !== undefined ? actual - paceLimit : 0;
  const isOverPace = paceLimit !== undefined && actual > paceLimit;

  return (
    <div className="progress-item mb-10">
      <div className="flex justify-between items-baseline mb-3">
        <span className="font-bold text-lg">{label}</span>
        <span className="text-sm font-medium text-slate-500">
          <b className="text-slate-900">¥{actual.toLocaleString()}</b>
          {showDiff && paceLimit !== undefined && (
            <span className={diff <= 0 ? 'text-emerald-500 ml-2' : 'text-rose-500 ml-2'}>
              ({diff > 0 ? '+' : ''}¥{diff.toLocaleString()})
            </span>
          )}
          {" / ¥"}{budget.toLocaleString()}
        </span>
      </div>
      <div className="h-2.5 bg-slate-100 rounded-full relative">
        <div 
          className={`h-full rounded-full transition-all duration-500 ${isOverPace ? 'bg-amber-500' : 'bg-indigo-600'}`} 
          style={{ width: `${percentage}%` }}
        />
        {pacePercentage !== null && (
          <div 
            className="pace-marker absolute top-[-5px] w-0.5 h-5 bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]" 
            style={{ left: `${pacePercentage}%` }}
          />
        )}
      </div>
    </div>
  );
};

export default ProgressBar;
```

- [ ] **Step 4: テストの実行と通過の確認**

Run: `cd frontend && npm test -- --run`
Expected: PASS

- [ ] **Step 5: コミット**

```bash
git add frontend/src/components/ProgressBar.tsx frontend/src/components/__tests__/ProgressBar.test.tsx
git commit -m "feat: enhance ProgressBar with pace marker and variance display"
```

---

### Task 2: MonthSelector コンポーネントの作成

**Files:**
- Create: `frontend/src/components/MonthSelector.tsx`
- Create: `frontend/src/components/__tests__/MonthSelector.test.tsx`

- [ ] **Step 1: テストの作成**

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import MonthSelector from '../MonthSelector';

describe('MonthSelector', () => {
  it('displays current month and triggers change', () => {
    const onChange = vi.fn();
    render(<MonthSelector currentMonth="2026-06" onChange={onChange} />);
    expect(screen.getByText('2026年 6月')).toBeInTheDocument();
    fireEvent.click(screen.getByText('◀'));
    expect(onChange).toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: テストの実行と失敗の確認**

Run: `cd frontend && npm test -- --run`
Expected: FAIL

- [ ] **Step 3: コンポーネントの実装**

```typescript
import React from 'react';

interface MonthSelectorProps {
  currentMonth: string; // YYYY-MM
  onChange: (newMonth: string) => void;
}

const MonthSelector: React.FC<MonthSelectorProps> = ({ currentMonth, onChange }) => {
  const [year, month] = currentMonth.split('-').map(Number);
  
  const handlePrev = () => {
    const d = new Date(year, month - 2);
    onChange(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`);
  };

  const handleNext = () => {
    const d = new Date(year, month);
    onChange(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`);
  };

  return (
    <div className="flex items-center gap-3 bg-indigo-50 px-4 py-2 rounded-full">
      <button onClick={handlePrev} className="text-indigo-600 font-bold hover:opacity-70">◀</button>
      <span className="text-indigo-600 font-bold text-sm min-w-[90px] text-center">
        {year}年 {month}月
      </span>
      <button onClick={handleNext} className="text-indigo-600 font-bold hover:opacity-70">▶</button>
    </div>
  );
};

export default MonthSelector;
```

- [ ] **Step 4: テストの実行と通過の確認**

Run: `cd frontend && npm test -- --run`
Expected: PASS

- [ ] **Step 5: コミット**

```bash
git add frontend/src/components/MonthSelector.tsx frontend/src/components/__tests__/MonthSelector.test.tsx
git commit -m "feat: add MonthSelector component"
```

---

### Task 3: KPIハイライト (StatGroup) の実装

**Files:**
- Create: `frontend/src/components/StatGroup.tsx`
- Modify: `frontend/src/pages/Dashboard.tsx`

- [ ] **Step 1: StatGroup コンポーネントの実装**

```typescript
import React from 'react';

interface StatProps {
  label: string;
  value: string;
  subValue?: string;
  colorClass?: string;
}

export const StatItem: React.FC<StatProps> = ({ label, value, subValue, colorClass }) => (
  <div className="flex flex-col">
    <span className="text-[10px] uppercase tracking-widest text-slate-400 font-bold mb-3">{label}</span>
    <span className={`text-4xl font-black tracking-tighter leading-none ${colorClass || 'text-slate-900'}`}>{value}</span>
    {subValue && <span className="text-xs font-semibold text-slate-500 mt-3">{subValue}</span>}
  </div>
);

const StatGroup: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="grid grid-cols-1 md:grid-cols-3 gap-16 mb-20">
    {children}
  </div>
);

export default StatGroup;
```

- [ ] **Step 2: コミット**

```bash
git add frontend/src/components/StatGroup.tsx
git commit -m "feat: add StatGroup and StatItem for non-card KPI display"
```

---

### Task 4: Dashboard ページの全面レイアウト刷新

**Files:**
- Modify: `frontend/src/pages/Dashboard.tsx`
- Modify: `frontend/src/App.css` (デザイン調整用)

- [ ] **Step 1: Dashboard ページの状態管理とレイアウト更新**

- [ ] **Step 2: 動作確認**

Run: `npm run build` (型チェック)
Check: `http://localhost:5173` で意図したレイアウトになっているか。

- [ ] **Step 3: コミット**

```bash
git add frontend/src/pages/Dashboard.tsx frontend/src/App.css
git commit -m "feat: overhaul Dashboard layout with document flow and pacemaker"
```

---

### Task 5: 資産チャートの統合

**Files:**
- Modify: `frontend/src/pages/Dashboard.tsx`
- Modify: `frontend/src/components/AssetChart.tsx`

- [ ] **Step 1: 資産チャートの配置（非カード形式）**

- [ ] **Step 2: フルリグレッションテストの実行**

Run: `python tools/cli.py qa regression`
Expected: ALL PASS (Backend + Frontend)

- [ ] **Step 3: コミット**

```bash
git add frontend/src/pages/Dashboard.tsx
git commit -m "feat: integrate asset charts into the new dashboard layout"
```
