# fix-001 — Fix frontend test regressions

## Context files (read for understanding — do not modify)
- frontend/src/pages/Dashboard.tsx — New structure using TopHeader
- frontend/src/components/TopHeader.tsx — Definition of the new header
- frontend/src/components/ProgressBar.tsx — New semantic classes

## Reference files (STRICT STYLE MATCH)
- AGENTS.md — Styling and testing conventions

## Required Skills
- none

## Files to create/modify (suggested)
- frontend/src/test/Dashboard.test.tsx — modify (update text assertion)
- frontend/src/components/__tests__/ProgressBar.test.tsx — modify (update class assertions)

## Description
The dashboard layout overhaul introduced new components and semantic CSS classes that broke existing unit tests. 
1. `Dashboard.test.tsx` expects "Kakeibo-ai" which was moved to the Sidebar (not part of the Dashboard unit test). Update it to expect "ダッシュボード" or "合計支出".
2. `ProgressBar.test.tsx` expects legacy Tailwind background classes. Update it to expect semantic classes like `warning` (for over-pace) or the base `progress-bar` class.

## Acceptance
- [ ] `frontend/src/test/Dashboard.test.tsx` passes
- [ ] `frontend/src/components/__tests__/ProgressBar.test.tsx` passes
- [ ] `python tools/cli.py qa regression` (frontend part) passes

## Needs tests
yes | tool = vitest, location = frontend/src/test/

---

## Implementation log (filled by dev after successful commit)
- Commit: ffee490 — fix(dashboard-layout-fix): fix frontend test regressions due to layout and styling changes
- Files modified:
  - frontend/src/components/__tests__/ProgressBar.test.tsx (modified)
  - frontend/src/test/Dashboard.test.tsx (modified)
- Tests added: none required
- Context & Reference files read:
  - frontend/src/pages/Dashboard.tsx
  - frontend/src/components/TopHeader.tsx
  - frontend/src/components/ProgressBar.tsx
  - AGENTS.md
- Notes: Used project's venv to run regression tests as 'typer' was missing in system python. Both vitest and full regression passed.
