# Scope: Dashboard Fix (Month Selection & Performance)

## Objective
Enable users to accurately view and manage their household budget by fixing month selection synchronization and improving dashboard performance by decoupling slow AI detection.

## User stories
- As a user, I want the dashboard to display data for the selected month so that I can track my expenses accurately.
- As a user, I want the dashboard to load quickly so that I don't have to wait to see my financial status.
- As a user, I want to switch between weekly and monthly budget views in the budget management section so that I can analyze my spending at different granularities.
- As a user, I want to click on weekly performance icons to view details for that specific week so that I can quickly investigate budget deviations.

## Acceptance criteria
- [ ] Removes the timeframe selector from the global dashboard header.
- [ ] Displays data for the month selected in the `MonthSelector` across all dashboard components (KPIs, Budget-Actual, Sankey).
- [ ] Implements a timeframe selector (Weekly/Monthly) within the `BudgetPacemaker` component.
- [ ] Updates the `BudgetPacemaker` view to filter by a specific week when a win/loss icon is clicked in the `WeeklyForm`.
- [ ] Decouples AI expense detection from the initial dashboard load to ensure immediate visibility of core financial data.
- [ ] Backend endpoints (`kpi`, `budget-actual`, `cash-flow`) correctly handle `month` and `timeframe` query parameters.
- [ ] Frontend API calls include the correctly selected `month` and `timeframe` parameters.

## External Tools & Design Mocks
- Figma: none
- Other Tools: none

## Reference Files (Gold Standards)
- src/api/routers/dashboard.py — Gold Standard for dashboard API.
- frontend/src/pages/Dashboard.tsx — Gold Standard for dashboard UI.
- frontend/src/api/client.ts — API client and type definitions.

## Architecture constraints
- Backend: FastAPI/SQLite using existing patterns.
- Frontend: React with Lucide icons.
- Avoid blocking initial page load with slow AI requests.

## Reuse (do NOT recreate)
- src/api/utils.py — for DB and budget utility functions.

## Out of scope
- Implementation of new AI detection models.
- Modification of data import or fetching logic.
- Changes to the main navigation menu outside of the dashboard header.

## Unverified assumptions (RISK)
- "Accessing that week's budget" via `WeeklyForm` assumes we will update the `BudgetPacemaker` view to show data for the specific week corresponding to the clicked icon.
- Backend support for arbitrary week filtering needs to be implemented or refined in `get_budget_actual`.

## Context
The dashboard currently suffers from synchronization issues where the month selector does not correctly filter all components, leading to confusing data displays. Additionally, slow AI detection processes are blocking the initial page load, degrading user experience. This update focuses on fixing these synchronization bugs and optimizing the critical rendering path for better performance.
