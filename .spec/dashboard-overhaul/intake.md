# Intake: Dashboard Overhaul

## PR target branch
staging

## Raw prompt
ダッシュボードについて以下の改善を行ってください。
・Total Expense: 桁数が多い場合にレイアウトが崩れるため、9桁まで表示してもレイアウト崩れが起こらないようにフォントサイズを小さくする。マージンをとる等の対策をしてください。
・円グラフ: 色合いが単調なのと、文字色が背景と同系色なので見づらいです。円グラフは色分けを行い、文字色は白にしてください。
・Cash Flow: 円グラフと同じく色合いを調整してください。また、各収支の金額と名前を表示してください。(今はマウスホバーしないと表示されません)また、収入の部分がMoneyforwardとなっているので、給与所得・現金貯蓄・投信などカテゴリで分けてください。
・予算管理のセクションの幅を増やして大きく表示ください。また、勝敗判定のロジックを見直してください。
・AI立替検知:根拠を記載しているテキストとMARKボタンが被っています。

改修・テストが完了したら、DEV環境でデータ含め確認できるようにしてください。データは本番データと同期してください。

## Clarifications (Q&A)
### Q1 — Feature behavior: Cash Flow (Sankey Chart) labels and colors
**Recommended:** Display Name + Amount on nodes, and use color coding for boxes.
**User answered:** "その方式でお願いします。箱の色分けもお願いします。このソースコードが参考になると思います。(https://github.com/team-mirai/marumie)"

### Q2 — Feature behavior: Budget win/loss logic
**Recommended:** Use only "Variable Expenses" for the weekly win/loss calculation to provide better feedback on daily spending.
**User answered:** "やりくり費のみでお願いします"

### Q3 — Feature behavior: AI Reimbursement layout
**Recommended:** Restrict text width (adding margin) to avoid overlap with the "MARK" button.
**User answered:** "テキストの幅を制限するようにしてください。"

### Q4 — Feature behavior: Chart colors
**Recommended:** Use a vivid color set to improve visibility.
**User answered:** "ビビットカラーでお願いします。"

## Confirmed feature behavior
- **Total Expense Layout:** Shrink font/adjust margin for up to 9 digits (¥100,000,000+).
- **Pie Chart Improvements:** Multi-color vivid palette, white text labels.
- **Sankey Chart (Cash Flow):** 
    - Always display Name + Amount on nodes.
    - Color-coded boxes (nodes).
    - Vivid colors.
    - Categorize income into "Salary", "Savings", "Investment", etc. instead of just "Moneyforward".
- **Budget Section:** Increase width in layout.
- **Budget Logic:** Weekly win/loss should only consider variable expenses (やりくり費).
- **AI UI:** Prevent text overlap with MARK button by restricting text width.
- **Data Sync:** Synchronize (anonymized) production data to DEV environment for verification.

## Reference Files (confirmed by user)
- `frontend/src/pages/Dashboard.tsx` — Main layout.
- `frontend/src/components/AssetPieChart.tsx` — Pie chart implementation.
- `frontend/src/components/SankeyChart.tsx` — Cash flow chart implementation.
- `src/api/routers/dashboard.py` — Backend for Sankey data and budget.
- `src/api/routers/analysis.py` — Weekly win/loss logic (`get_weekly_form`).
- `tools/ops/sync_prod_to_staging.py` — Reference for data sync.

## Architecture constraints (confirmed)
- Follow existing React/Tailwind/FastAPI pattern.
- Vivid color palette for all charts.
- White text for chart labels.

## Reuse (do NOT recreate)
- `Sankey` from `recharts` (customized).
- `sync_prod_to_staging.py` logic for data sync.

## Unverified assumptions (RISK)
- The exact color codes for "vivid" palette are not specified; I will use a high-contrast set.
- Income categorization depends on the data having proper `category` or `source` values beyond just "Moneyforward". I will need to map these in the backend.
