# 001 — Dashboard Layout & Overview Overhaul

## Context files (read for understanding — do not modify)
- frontend/src/pages/Dashboard.tsx — Current implementation to be overhauled.
- frontend/src/index.css — CSS variables and global styles.
- conductor/ui-overhaul-plan.md — Target design specifications.

## Reference files (STRICT STYLE MATCH)
- conductor/ui-overhaul-plan.md — Visual and structural "Gold Standard".

## Required Skills
- none

## Files to create/modify (suggested)
- frontend/src/pages/Dashboard.tsx — modify (overhaul main layout and Overview section)

## Description
Remove all `.card` classes and associated `dashboard-grid` layout from `Dashboard.tsx`. Implement a "flowing document" structure using Tailwind utility classes for spacing (`mb-16`, `mb-24`).
Specifically, overhaul the **Overview section** (top of the page):
- Display "Total Expense", "Daily Average", and "Kakeibo Score" using massive font sizes (e.g., `text-7xl font-black` for the primary metric).
- Arrange these KPIs in a high-density horizontal layout.
- Integrate the `AssetPieChart` (donut chart) on the right side of this Overview section, aligned with the KPIs.

## Acceptance
- [ ] Dashboard container no longer uses card-based borders or backgrounds for the main sections.
- [ ] Overview section features huge typography for the three key metrics.
- [ ] Asset donut chart is positioned to the right of the KPIs in the Overview section.
- [ ] Layout follows the Slate-950 base theme with Indigo/Amber/Emerald accents as defined in `index.css`.

## Needs tests
yes | tool = npm run build (frontend), location = frontend/

## Implementation log (filled by dev after successful commit)
- Commit: 9a8f70c44d81de17369a19c8b2ba35ee0c26fe14 — feat(dashboard-overhaul-alignment): overhaul main layout and Overview section
- Files modified:
  - frontend/src/pages/Dashboard.tsx (modified)
- Tests added: none required (verified with npm run build)
- Context & Reference files read: 
  - frontend/src/pages/Dashboard.tsx
  - frontend/src/index.css
  - conductor/ui-overhaul-plan.md
- Notes: Removed unused StatItem import to fix build error. Overhauled the entire layout of Dashboard.tsx to remove .card classes and implement the flowing document style with massive typography in the Overview section.
