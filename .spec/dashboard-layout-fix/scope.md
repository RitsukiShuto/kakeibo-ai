# Scope: Dashboard Layout Fix

## Objective
Enable users to view a correctly formatted dashboard by fixing layout collapses and visual bugs in `Dashboard.tsx` so that the UI remains usable and consistent with the dark theme.

## User stories
- As a user, I want the dashboard text to be readable on a dark background so that I can see my financial status clearly.
- As a user, I want the dashboard elements to use a consistent theme so that the UI looks polished and professional.
- As a user, I want the dashboard to be responsive so that it works well on different screen sizes.

## Acceptance criteria
- [ ] Displays all text clearly (no invisible text due to dark background, e.g., in `StatItem` and `ProgressBar`).
- [ ] Replaces high-contrast/legacy light theme elements (e.g., `bg-slate-100`, `border-slate-100` in `BudgetPacemaker` and `ProgressBar`) with theme-consistent styles.
- [ ] Persists the current React component structure in `Dashboard.tsx`.
- [ ] Applies global theme tokens and classes from `index.css` (e.g., `.card`, `.kpi-card`, `.dashboard-grid`) or uses appropriate CSS variables.
- [ ] Adjusts layout correctly across different screen widths (responsive behavior).

## External Tools & Design Mocks
- Figma: none
- Other Tools: none

## Reference Files (Gold Standards)
- `frontend/src/index.css` — Gold Standard for theme tokens, global classes (`.card`, `.main-content`), and CSS variables.
- `frontend/src/pages/Dashboard.tsx` — The file to be fixed.
- `docs/archive/dashboard_prototype/index.html` — Reference for spacing and general aesthetic intent, although the current component structure is prioritized.

## Architecture constraints
- Maintain the current React component structure in `Dashboard.tsx`.
- Prioritize CSS classes from `index.css` over raw Tailwind utilities where they overlap.
- Ensure compatibility with the global dark theme.

## Reuse (do NOT recreate)
- Use CSS variables defined in `:root` of `index.css` (e.g., `var(--text-main)`, `var(--border)`, `var(--card-bg)`).

## Out of scope
- No changes to backend API or data fetching logic.
- No new features or dashboard widgets.
- No migration to a different UI library (staying with current Tailwind + custom CSS).

## Unverified assumptions (RISK)
- none

## Context
The dashboard was recently modified, but some elements are still using legacy light-theme styles or hardcoded colors that clash with the new dark-themed UI. This results in invisible text and inconsistent borders. Fixing these visual regressions is critical for the dashboard's usability.
