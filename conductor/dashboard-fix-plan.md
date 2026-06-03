# Dashboard Fixes Implementation Plan

## Objective
Fix the dashboard month selection bug and improve initial loading performance. Remove the global timeframe selector and implement localized timeframe/week switching for the budget management section.

## Scope & Impact
- **Backend (`src/api/routers/dashboard.py`, `src/api/routers/analysis.py`)**: Update endpoints to filter data based on the provided `month` and `week` parameters. Include budget `section` metadata.
- **Frontend (`frontend/src/pages/Dashboard.tsx`, `frontend/src/components/...`)**: Remove global timeframe tabs. Localize timeframe state to the Budget components. Decouple slow AI reimbursement detection from the initial data load to improve perceived performance. Link the Weekly win/loss form to budget views.

## Proposed Solution (Design)
1. **Backend Parameterization**: Ensure `get_kpi`, `get_budget_actual`, `get_stats_flow`, and `get_weekly_form` accurately respect the `month` parameter.
2. **AI Decoupling**: Move the `/api/expense-splitter/detect` API call out of the initial `Promise.all` block in `Dashboard.tsx`. Fetch it asynchronously after core financial data renders.
3. **Localized Timeframe Control**: Remove the timeframe prop from `TopHeader`. Add it directly to `BudgetPacemaker`.
4. **Data-driven Sections**: Update the `budget-actual` API to return category section (fixed/variable) metadata to remove hardcoded UI lists.

## Implementation Steps

### Task 1: Backend API Enhancement
- Update `src/api/routers/dashboard.py` to support historical data retrieval via `month` query parameter for KPI, Budget-Actual, and Stats Flow endpoints.
- Ensure `get_budget_actual` can filter by a specific `week`.
- Update `get_budget_actual` response to include the `section` (fixed/variable) field based on the loaded budget configuration.

### Task 2: Frontend Dashboard State & Sync
- In `frontend/src/pages/Dashboard.tsx`, ensure `MonthSelector` changes trigger a re-fetch of all relevant data for that specific month.
- Remove the timeframe selector from `TopHeader`.
- Update the filtering logic for `variableExpenses` and `fixedExpenses` to use the new `section` field from the API instead of a hardcoded list.

### Task 3: Weekly View Filtering
- In `frontend/src/components/WeeklyForm.tsx`, add click handlers to the week icons (W/L/D).
- In `frontend/src/pages/Dashboard.tsx`, pass a callback to `WeeklyForm` to update a new `selectedWeek` state when clicked. Trigger a re-fetch of `BudgetActual` data for that specific week and update the `BudgetPacemaker` view.

### Task 4: Performance Optimization
- In `frontend/src/pages/Dashboard.tsx`, remove the `expense-splitter/detect` POST request from the main `fetchData` function's `Promise.all`.
- Create a separate `useEffect` or background function to fetch the AI reimbursement suggestions after the main data has loaded, updating the `reimbursementSuggestions` state independently.

## Verification & Testing
- Run `pytest tests/test_dashboard_api.py` to ensure backend parameter filtering works.
- Run `npm run build` in `frontend/` to verify TypeScript types and build success.
- End-to-end manual verification in the browser to ensure month switching works, performance is improved, and weekly filtering functions correctly.
