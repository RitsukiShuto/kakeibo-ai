# Design: Dashboard Overhaul Alignment

## Existing conventions honored
- Source of truth: `AGENTS.md`
- Language & framework: React, TypeScript, Tailwind CSS
- Folder structure pattern: `frontend/src/pages/`, `frontend/src/components/`
- Naming conventions: PascalCase for components, camelCase for props/state.
- State / data-flow pattern: standard React `useState`/`useEffect` with `axios` (via `client.ts`).
- Testing setup: `pytest` for backend, `npm run build` for frontend verification (per `AGENTS.md` Tier 2).
- Specific rules being honored: "Abolish card-based containment" (per `ui-overhaul-plan.md`), "Vibrant Minimalist" philosophy (Slate-950 base, Indigo/Amber/Emerald accents).

## Technical approach
The overhaul transforms the dashboard from a grid of cards into a single "flowing document". `Dashboard.tsx` will be restructured to remove the `.card` wrappers, instead using ample whitespace, large-scale typography, and subtle divider lines to achieve a high-density layout. The Overview section will feature high-impact KPIs with varying font sizes (6xl-7xl) and an integrated donut chart. Components like `BudgetPacemaker` and `SankeyChart` will be adjusted to occupy full width or balanced columns without contained backgrounds, using the Indigo, Amber, and Emerald accent colors for semantic emphasis.

## Modules / components touched
- `Dashboard.tsx` — Main layout overhaul, removing card classes and restructuring sections into a flowing document.
- `BudgetForm.tsx` — Renamed to `WeeklyForm.tsx` (suggested) to match its purpose as a W/L/D win/loss display.
- `BudgetPacemaker.tsx` — Layout adjustments to fit the document style, ensuring timeframe toggles and progress bars align with the high-density requirement.
- `ProgressBar.tsx` — Styling updates for high-density and ensuring the "Pace Limit" marker is visually prominent.
- `SankeyChart.tsx` — Height and padding adjustments for full-width display (h-[450px]).

## Patterns / abstractions
- **Flowing Document**: Replaces card-based grids with semantic sections separated by whitespace (`mb-16`, `mb-24`) and horizontal rules (`h-px`).
- **Massive Typography**: Uses extreme Tailwind utility classes (`text-7xl font-black`) to create visual hierarchy and instant scannability for KPIs.
- **Accent-driven Semantics**: Uses the project's defined Indigo (Primary), Amber (Warning/Budget), and Emerald (Success/Score) colors for visual focus.

## Trade-offs
- **Inlining vs Componentization**: Chose to inline some KPI layouts in `Dashboard.tsx` instead of using a generic `StatItem` component to allow for unique typographic scaling and spacing that varies per metric.
- **Misnamed Component**: Renaming `BudgetForm` to `WeeklyForm` is preferred as the current name is misleading (it displays history, doesn't act as a form), aligning with the `ui-overhaul-plan.md` terminology.

## Out of scope (technical)
- Backend API modifications (assumed support for `/api/stats/flow` and `/api/analysis-history/form`).
- Transactions page or Settings page overhaul.
- New data visualizations beyond those specified in `scope.md`.

## Gaps for human attention
- Ensure the backend actually returns `pace_limit` in the `BudgetActual` items for the orange line to appear.
