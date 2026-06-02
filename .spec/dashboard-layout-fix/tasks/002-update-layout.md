# 002 — Update Dashboard header and container layout

## Context files (read for understanding — do not modify)
- frontend/src/components/TopHeader.tsx — Standard header component.
- frontend/src/App.tsx — Main app layout structure.

## Reference files (STRICT STYLE MATCH)
- frontend/src/index.css — For `.dashboard-grid` and container classes.

## Files to create/modify (suggested)
- frontend/src/pages/Dashboard.tsx — modify (switch to TopHeader and .dashboard-grid)

## Description
Refactor the high-level layout of `Dashboard.tsx`. Replace the custom header with the `TopHeader` component. Remove redundant logo/text that is already present in the Sidebar. Change the main page container to use the `.dashboard-grid` class from `index.css`.

## Acceptance
- [ ] `Dashboard.tsx` uses `TopHeader` for title and refresh actions.
- [ ] Redundant "Kakeibo-ai" logo is removed from the page header.
- [ ] Main content area uses `.dashboard-grid` class.
- [ ] Loading screen uses theme-consistent background color (`var(--bg-color)`).

## Needs tests
no

---

## Implementation log (filled by dev after successful commit)
- Commit: 17dc4c4e6e4424cfffebf61f002dfc711abfdab7 — feat(dashboard-layout-fix): update dashboard header and container layout
- Files modified:
  - frontend/src/pages/Dashboard.tsx (modified)
- Tests added: none required
- Context & Reference files read: 
  - frontend/src/components/TopHeader.tsx
  - frontend/src/App.tsx
  - frontend/src/index.css
- Notes: Moved MonthSelector to content area as a contextual control. Used TopHeader for title, refresh, and timeframe selection. Switched main container to .dashboard-grid.

