# Design: Dashboard Layout Fix

## Existing conventions honored
- Source of truth: `AGENTS.md` and `index.css` (Reference File)
- Language & framework: React + TypeScript + Tailwind CSS
- Folder structure pattern: Component-based (`frontend/src/components` and `frontend/src/pages`)
- Naming conventions: PascalCase for components and props
- State / data-flow pattern: standard React `useState`/`useEffect` hooks
- Testing setup: `pytest` for backend (out of scope); frontend builds verified via `npm run build`
- Specific rules being honored: 
    - "Prioritize CSS classes from `index.css` over raw Tailwind utilities where they overlap." (from `scope.md`)
    - "Use CSS variables defined in `:root` of `index.css` (e.g., `var(--text-main)`, `var(--border)`, `var(--card-bg)`)." (from `scope.md`)

## Technical approach
The goal is to align `Dashboard.tsx` and its sub-components with the global dark theme and grid system defined in `index.css`. This will be achieved by:
1.  **Token replacement**: Replacing hardcoded Tailwind `slate` color classes (e.g., `bg-slate-100`, `text-slate-900`) with CSS variables (`var(--text-main)`, `var(--border)`, etc.) or semantic theme classes.
2.  **Component standardization**: Updating `StatItem`, `BudgetPacemaker`, and `ProgressBar` to use classes defined in `index.css` (like `.progress-bar-container`, `.progress-bar`, `.card`).
3.  **Layout restructuring**: Updating `Dashboard.tsx` to use the 12-column `.dashboard-grid` and the standard `TopHeader` component, ensuring the layout is responsive and consistent with the intended project aesthetic.
4.  **Grid alignment**: Mapping dashboard sections to the predefined grid area classes (`section-budget`, `section-ai-review`, etc.) in `index.css`.

## Modules / components touched
- `StatItem.tsx` (and `StatGroup.tsx`) — Updated to use theme-aware text colors and layout classes.
- `BudgetPacemaker.tsx` — Restyled to use theme-consistent borders and backgrounds.
- `ProgressBar.tsx` — Refactored to use `.progress-bar-container` and `.progress-bar` from `index.css`.
- `Dashboard.tsx` — Major layout overhaul to adopt `TopHeader` and `.dashboard-grid`.

## Patterns / abstractions
- **Theme Variables**: Systematic use of CSS variables for consistency across theme switches (if any) and ease of maintenance.
- **Grid Areas**: Leveraging named grid classes from the global CSS to manage complex responsive layouts.

## Trade-offs
- **StatItem vs KPICard**: Chose to keep and fix `StatItem` instead of migrating to `KPICard` to preserve the existing `subValue` logic which provides more context than the current `KPICard` component, while ensuring its styling matches the `kpi-card` aesthetic.
- **Header integration**: Chose to use `TopHeader` for standard actions (refresh, timeframe) but will place `MonthSelector` as a contextual control within the page content to maintain functional parity without over-complicating `TopHeader`.

## Out of scope (technical)
- No backend API changes.
- No new features or dashboard widgets.
- No changes to `Transactions.tsx` or other pages unless they share affected components.

## Gaps for human attention
- none
