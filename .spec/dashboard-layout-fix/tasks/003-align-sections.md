# 003 — Align Dashboard sections with Grid system

## Context files (read for understanding — do not modify)
- docs/archive/dashboard_prototype/index.html — Reference for intended layout.

## Reference files (STRICT STYLE MATCH)
- frontend/src/index.css — For grid area classes (`section-budget`, etc.).

## Files to create/modify (suggested)
- frontend/src/pages/Dashboard.tsx — modify (apply grid area classes to sections)

## Description
Map the existing dashboard sections to the 12-column grid system. Apply named grid area classes from `index.css` (e.g., `section-budget`, `section-ai-review`, `section-transactions`) to the appropriate section wrappers. Ensure each major section is wrapped in a `.card` class for consistent visual styling.

## Acceptance
- [ ] Sections are correctly assigned to grid areas (e.g., Transactions span full width, AI Review and Budget side-by-side on desktop).
- [ ] Each section has a consistent `.card` appearance.
- [ ] Spacing between sections follows the `gap-24` (or `gap-6`) standard from `index.css`.

## Needs tests
no

---

## Implementation log (filled by dev after successful commit)
- Commit: 347ec3d2ef858869f0a393d016f7b83b60436d83 — feat(dashboard-layout-fix): align dashboard sections with grid system
- Files modified:
  - frontend/src/pages/Dashboard.tsx (modified)
- Tests added: none required
- Context & Reference files read:
  - docs/archive/dashboard_prototype/index.html
  - frontend/src/index.css
- Notes: Removed unused 'StatGroup' import from Dashboard.tsx. Applied theme variables (e.g., var(--primary-light), var(--success)) to StatItems. Unified section headers with Lucide icons.
