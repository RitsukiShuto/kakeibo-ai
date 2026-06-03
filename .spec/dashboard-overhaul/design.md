# Design: Dashboard Overhaul

## Existing conventions honored
- Source of truth: both AGENTS.md and CLAUDE.md (via GEMINI.md context)
- Language & framework: React (TypeScript) for frontend, FastAPI (Python) for backend (AGENTS.md section "サブエージェント別・作業フロー").
- Folder structure pattern: `frontend/src/` for React components, `src/api/routers/` for FastAPI endpoints (AGENTS.md section "ディレクトリ構成と役割").
- Naming conventions: CamelCase for React components, snake_case for Python files and functions.
- State / data-flow pattern: React `useEffect`/`useCallback` with Axios client for data fetching.
- Testing setup: `pytest` for backend, `python tools/cli.py qa regression` for full validation (AGENTS.md section "テスト戦略").
- Specific rules being honored: TDD approach, environment separation (development in `dev_local/`), security and QA review requirements.

## Technical approach
The overhaul focuses on layout stability, chart readability, and budget logic accuracy. 
- **Layout**: `Dashboard.tsx` will be adjusted to handle up to 9-digit amounts by scaling font sizes and increasing the Budget section's width (using a 7:5 grid ratio). 
- **Charts**: A new high-contrast "Vivid Palette" will be applied to all charts to improve category differentiation. `SankeyChart.tsx` will be enhanced with a custom node renderer to display static labels with amounts.
- **Logic**: The backend `analysis` router will be updated to filter "win/loss" calculations strictly for `variable` expenses (やりくり費), and the `dashboard` router will map generic income sources (e.g., Moneyforward) to specific categories like "Salary" or "Investment" based on transaction metadata.
- **Data Parity**: A new synchronization script will be added to `tools/ops/` to allow developers to safely import anonymized production data into their local environment for realistic verification.

## Modules / components touched
- `Dashboard.tsx` — layout adjustments (Total Expense, grid spans, AI reimbursement width)
- `AssetPieChart.tsx` — vivid color palette implementation
- `SankeyChart.tsx` — custom node rendering for labels/amounts and color palette
- `src/api/routers/analysis.py` — budget win/loss logic filtering (variable expenses)
- `src/api/routers/dashboard.py` — Sankey income source mapping logic
- `tools/ops/sync_prod_to_dev.py` — new tool for production data synchronization

## Patterns / abstractions
- Reused `sync_prod_to_staging.py` logic for the new `sync_prod_to_dev.py` tool.
- Introduced a shared `VIVID_PALETTE` constant for chart consistency.
- No new complex abstractions required; extending existing component props and backend filters.

## Trade-offs
- Chose `lg:col-span-7` for Budget and `lg:col-span-5` for Transactions (from 6:6) to give Budget more space while keeping the Transaction list readable without horizontal scroll.
- Chose to map "Moneyforward" income sources in the backend rather than the frontend to keep the Sankey data processing centralized and easier to test.

## Out of scope (technical)
- Refactoring the entire `Dashboard.tsx` into smaller sub-components (only modifying existing sections).
- Adding real-time data synchronization (one-time manual sync is sufficient per scope).
- Modifying the DB schema (mapping is done at the API layer).

## Gaps for human attention
- The exact mapping rules for "Moneyforward" income to "Salary/Savings/Investment" depend on the user's specific `category` or `genre` usage in Moneyforward. I will implement a sensible default mapping based on common patterns.
