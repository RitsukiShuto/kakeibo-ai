# Scope: Dashboard Overhaul

## Objective
Enhance the dashboard UI and logic to improve readability, layout stability for large amounts, and budget accuracy while ensuring the development environment is synchronized with production-like data for verification.

## User stories
- As a user, I want the Total Expense display to remain readable even with large amounts (up to 9 digits) so that the layout doesn't break.
- As a user, I want charts to have a vivid color palette and clear white text so that I can easily distinguish categories.
- As a user, I want the Cash Flow chart to show names and amounts clearly and categorized by income source so that I can understand my finances at a glance.
- As a user, I want the budget section to be larger and reflect my actual spending habits (variable expenses) so that the win/loss feedback is more meaningful.
- As a user, I want the AI reimbursement UI to be clean and readable without text overlapping buttons.
- As a developer, I want the DEV environment to have synchronized production-like data so that I can verify the fixes with realistic scenarios.

## Acceptance criteria
- [ ] Total Expense font size scales down or margins adjust to accommodate up to 9 digits (¥100,000,000+) without overlapping other elements.
- [ ] Pie charts use a vivid color palette and display labels in white text.
- [ ] Cash Flow (Sankey) chart nodes display both name and amount without hovering.
- [ ] Cash Flow (Sankey) chart nodes are color-coded using a vivid palette.
- [ ] Cash Flow (Sankey) chart categorizes income into "Salary", "Savings", "Investment", etc., instead of showing "Moneyforward".
- [ ] Budget section width is increased in the dashboard layout.
- [ ] Budget win/loss logic only considers variable expenses (やりくり費).
- [ ] AI Reimbursement text width is restricted to prevent overlap with the "MARK" button.
- [ ] Production data is synchronized to the DEV environment for verification.

## External Tools & Design Mocks
- Figma: none
- Other Tools: https://github.com/team-mirai/marumie (Sankey reference)

## Reference Files (Gold Standards)
- `frontend/src/pages/Dashboard.tsx` — Main layout.
- `frontend/src/components/AssetPieChart.tsx` — Pie chart implementation.
- `frontend/src/components/SankeyChart.tsx` — Cash flow chart implementation.
- `src/api/routers/dashboard.py` — Backend for Sankey data and budget.
- `src/api/routers/analysis.py` — Weekly win/loss logic (`get_weekly_form`).
- `tools/ops/sync_prod_to_staging.py` — Reference for data sync.

## Architecture constraints
- Follow existing React/Tailwind/FastAPI pattern.
- Vivid color palette for all charts.
- White text for chart labels.

## Reuse (do NOT recreate)
- `Sankey` from `recharts` (customized).
- `sync_prod_to_staging.py` logic for data sync.

## Out of scope
- Complete redesign of the dashboard beyond the specified components.
- Implementation of new data fetching sources (only mapping existing data).
- Real-time data sync (one-time sync for verification is enough).

## Unverified assumptions (RISK)
- The exact color codes for "vivid" palette are not specified; I will use a high-contrast set.
- Income categorization depends on the data having proper `category` or `source` values beyond just "Moneyforward". I will need to map these in the backend.

## Context
The user has reported several readability and layout issues with the dashboard as their financial data grows. Specifically, large expense amounts cause layout breaks, and the charts are hard to read due to poor color contrast. Additionally, the budget logic was too broad, and the user wants it focused on controllable (variable) expenses. Ensuring data parity between production and development is critical for verifying these UI/UX fixes.
