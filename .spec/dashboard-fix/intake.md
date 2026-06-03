# Intake: Dashboard Fix (Month Selection & Performance)

## PR target branch
staging

## Raw prompt
ダッシュボードに以下の不具合があるので修正してください。
・右上の月を選択してもその月のデータが表示されない(例えば5月を選んだ場合はその月の実績が表示されるハズ)
・画面を開くのに時間がかかる(原因はなんですか？)

User clarification:
- Q1.ヘッダ部の選択肢は削除してください。予実管理のところは週次と月次を切り替え可能にしてください。
　予実管理で週次を選択した際は勝敗表示を選択することでその週の予実にアクセスできるようにしてください。
- Q2.そのように修正してください。AIのコンテキスト浪費にもつながるので。 (Refers to moving AI detection out of main load)
- Q3.ありません

## Clarifications (Q&A)
### Q1 — Feature behavior: Timeframe selection and navigation
**Recommended:** Remove timeframe from header. Keep it local to Budget management.
**User answered:** Agreed. Remove header timeframe. Budget management should be switchable between weekly and monthly. Clicking win/loss in WeeklyForm should update the budget view for that week.

### Q2 — Performance: AI Detection bottleneck
**Recommended:** Remove AI detection from initial dashboard load to improve performance.
**User answered:** Agreed. This also saves AI context/tokens.

### Q3 — Reference files:
**Recommended:** `src/api/routers/dashboard.py` and `frontend/src/pages/Dashboard.tsx`.
**User answered:** None others.

## Confirmed feature behavior
- **Inputs:** `month` (YYYY-MM) query parameter for all dashboard-related backend endpoints.
- **KPI Endpoint:** Should filter by `month` and `timeframe`.
- **Budget-Actual Endpoint:** Should filter by `month` and `timeframe`.
- **Cash Flow (Sankey) Endpoint:** Should filter by `month`.
- **Performance:** `expense-splitter/detect` is moved to a separate loading state or triggered after main data load.
- **UI Changes:**
  - Header timeframe selector removed.
  - `BudgetPacemaker` gets its own timeframe selector (Weekly/Monthly).
  - `WeeklyForm` items are clickable to filter `BudgetPacemaker` by that specific week.
  - Selected `month` from `MonthSelector` is applied to all relevant API calls.

## Reference Files (confirmed by user)
- `src/api/routers/dashboard.py` — Gold Standard for dashboard API.
- `frontend/src/pages/Dashboard.tsx` — Gold Standard for dashboard UI.
- `frontend/src/api/client.ts` — API client and type definitions.

## Architecture constraints (confirmed)
- Backend: FastAPI/SQLite using existing patterns.
- Frontend: React with Lucide icons.
- Avoid blocking initial page load with slow AI requests.

## Reuse (do NOT recreate)
- `src/api/utils.py` — for DB and budget utility functions.

## Unverified assumptions (RISK)
- "Accessing that week's budget" via `WeeklyForm` assumes we will update the `BudgetPacemaker` view to show data for the specific week corresponding to the clicked icon.
- Backend support for arbitrary week filtering needs to be implemented or refined in `get_budget_actual`.
