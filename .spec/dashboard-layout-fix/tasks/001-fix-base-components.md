# 001 — Fix base component styling for theme consistency

## Context files (read for understanding — do not modify)
- frontend/src/index.css — Theme tokens and global styles.

## Reference files (STRICT STYLE MATCH)
- frontend/src/index.css — The "Gold Standard" for theme tokens.

## Files to create/modify (suggested)
- frontend/src/components/StatGroup.tsx — modify (update colors and layout classes)
- frontend/src/components/BudgetPacemaker.tsx — modify (update colors and border classes)
- frontend/src/components/ProgressBar.tsx — modify (update to use .progress-bar-container and .progress-bar classes)

## Description
Update the core UI components used in the dashboard to use theme variables (`var(--text-main)`, `var(--border)`, etc.) instead of hardcoded Tailwind `slate` color classes. Ensure `StatItem` text is readable on dark backgrounds and `ProgressBar` uses the styles defined in `index.css`.

## Acceptance
- [ ] `StatItem` value text is readable (e.g., using `var(--text-main)` or `text-slate-100`).
- [ ] `ProgressBar` uses `.progress-bar-container` and `.progress-bar` from `index.css`.
- [ ] `BudgetPacemaker` uses theme-consistent borders (`var(--border)` or `border-slate-800`).

## Needs tests
no

---

## Implementation log (filled by dev after successful commit)
- Commit: 8a3dbe8 — fix(dashboard-layout-fix): apply theme consistency to base components
- Files modified:
  - frontend/src/components/BudgetPacemaker.tsx (modified)
  - frontend/src/components/ProgressBar.tsx (modified)
  - frontend/src/components/StatGroup.tsx (modified)
- Tests added: 0 (none) | none required
- Context & Reference files read:
  - frontend/src/index.css
- Notes: none
