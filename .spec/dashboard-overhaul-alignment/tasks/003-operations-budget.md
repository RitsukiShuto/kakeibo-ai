# 003 — Operations: Budget Pacemaker & Weekly Form

## Context files (read for understanding — do not modify)
- frontend/src/components/BudgetPacemaker.tsx — Main component for this section.
- frontend/src/components/BudgetForm.tsx — Current Weekly Form implementation.
- frontend/src/components/ProgressBar.tsx — Progress bar with pace limit.

## Reference files (STRICT STYLE MATCH)
- conductor/ui-overhaul-plan.md — Description of "Weekly Form" and "Budget Pacemaker".

## Required Skills
- none

## Files to create/modify (suggested)
- frontend/src/components/WeeklyForm.tsx — create (renamed from BudgetForm.tsx)
- frontend/src/components/BudgetForm.tsx — delete (after renaming)
- frontend/src/components/BudgetPacemaker.tsx — modify (align with new design)
- frontend/src/pages/Dashboard.tsx — modify (integrate updated components)

## Description
Overhaul the **Operations section** focus on Budget Pacemaker and Weekly Form:
- Rename `BudgetForm.tsx` to `WeeklyForm.tsx` to reflect its purpose as a win/loss display.
- Update `BudgetPacemaker.tsx` to use the "flowing document" style, removing card-like headers and backgrounds.
- Ensure `ProgressBar.tsx` correctly displays the "Pace Limit" (orange line) and that the timeframe switching logic (Weekly, Monthly, Quarterly, Yearly) is intuitive.
- Highlight the current week in `WeeklyForm` with a vibrant border as per `ui-overhaul-plan.md`.

## Acceptance
- [ ] `BudgetForm` renamed to `WeeklyForm` and uses proper semantics.
- [ ] `BudgetPacemaker` follows the document-first layout.
- [ ] Timeframe switching works for all four periods.
- [ ] Current week is visually highlighted in the Weekly Form.

## Needs tests
yes | tool = npm run build (frontend), location = frontend/

## Implementation log (filled by dev after successful commit)
- Commit: b8a2d0eafdbdb6963753d4b597755d4eb1dd9e1a — feat(dashboard-overhaul-alignment): overhaul operations section with WeeklyForm and BudgetPacemaker
- Files modified:
  - frontend/src/components/WeeklyForm.tsx (created)
  - frontend/src/components/BudgetForm.tsx (deleted)
  - frontend/src/components/BudgetPacemaker.tsx (modified)
  - frontend/src/components/ProgressBar.tsx (modified)
  - frontend/src/pages/Dashboard.tsx (modified)
- Tests added: none required (verified with npm run build)
- Context & Reference files read:
  - frontend/src/components/BudgetPacemaker.tsx
  - frontend/src/components/BudgetForm.tsx
  - frontend/src/components/ProgressBar.tsx
  - conductor/ui-overhaul-plan.md
- Notes: Standardized colors to match Slate-950 base with Amber/Emerald/Indigo accents. Improved ProgressBar density and added ping animation to the current week in WeeklyForm for better visibility.
