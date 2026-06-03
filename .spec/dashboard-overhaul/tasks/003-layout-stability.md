# 003 — Stabilize Dashboard layout & AI UI

## Context files (read for understanding — do not modify)
- frontend/src/pages/Dashboard.tsx — current layout and UI.

## Reference files (STRICT STYLE MATCH)
- frontend/src/pages/Dashboard.tsx — maintain the Tailwind utility pattern.

## Required Skills
- List any skills from scope.md that should be loaded for this task (none).

## Files to create/modify (suggested)
- frontend/src/pages/Dashboard.tsx — modify (Total Expense scaling, Grid spans, AI UI)

## Description
Improve layout stability and prevent overlaps:
1. In `Dashboard.tsx`, adjust the `Total Expense` font size (currently `text-5xl sm:text-6xl md:text-7xl`) to scale down properly for large amounts (up to 9 digits). Consider using `text-4xl sm:text-5xl md:text-6xl lg:text-7xl` or adding `break-all` / `overflow-hidden`.
2. Increase the width of the Budget section by changing the grid layout from `lg:col-span-6` / `lg:col-span-6` to `lg:col-span-7` (Budget) and `lg:col-span-5` (Transactions).
3. In the AI detection suggestions list, restrict the width of the text (reason/comment) or add `truncate` to prevent it from overlapping the "MARK" button. Ensure the button has a stable fixed width.

## Acceptance
- [ ] Total Expense (e.g., ¥123,456,789) fits within its container without breaking the layout on desktop and mobile.
- [ ] Budget section is visibly wider than the Recent Transactions section on large screens.
- [ ] AI detection reasons do not overlap the "Mark" button even with long text.

## Needs tests
no (UI manual verification)

---

## Implementation log (filled by dev after successful commit)
- Commit: 3b91db8387a92513476121987da938b6e8c879db — feat(dashboard-overhaul): stabilize dashboard layout and AI UI
- Files modified:
  - frontend/src/pages/Dashboard.tsx (modified)
- Tests added: none required (UI manual verification)
- Context & Reference files read:
  - frontend/src/pages/Dashboard.tsx
- Notes: none
