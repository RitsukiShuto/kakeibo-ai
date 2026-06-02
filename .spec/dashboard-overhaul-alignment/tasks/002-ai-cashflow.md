# 002 — AI Insights & Cash Flow Analysis

## Context files (read for understanding — do not modify)
- frontend/src/pages/Dashboard.tsx — Current implemented sections.
- frontend/src/components/SankeyChart.tsx — Chart component to be adjusted.

## Reference files (STRICT STYLE MATCH)
- conductor/ui-overhaul-plan.md — Specific height and style requirements for these sections.

## Required Skills
- none

## Files to create/modify (suggested)
- frontend/src/pages/Dashboard.tsx — modify (overhaul AI Insights and Cash Flow sections)
- frontend/src/components/SankeyChart.tsx — modify (adjust height and padding)

## Description
Overhaul the **AI Insights** and **Cash Flow** sections in `Dashboard.tsx`:
- AI Insights: Display as pure plain text (approx. 2 lines) without any background, border, or `.review-summary` box. Use an italic, high-contrast text style (e.g., `text-lg italic text-slate-300`).
- Cash Flow: Ensure the `SankeyChart` is full-width and has a height of approximately 450px (`h-[450px]`). Remove section headers that use `.card-header` styling, replaced by subtle label-and-line headers (e.g., `text-sm font-black text-slate-500 uppercase tracking-[0.2em]`).

## Acceptance
- [ ] AI Insights are rendered as plain text without containment.
- [ ] Cash Flow section is full-width and 450px high.
- [ ] Section dividers use subtle lines/spacing instead of card boundaries.

## Needs tests
yes | tool = npm run build (frontend), location = frontend/

## Implementation log (filled by dev after successful commit)
- Commit: 9951be8e46d85465ce9a37961969a278593c67c3 — feat(dashboard-overhaul-alignment): overhaul AI Insights and Cash Flow sections
- Files modified:
  - frontend/src/components/SankeyChart.tsx (modified)
  - frontend/src/pages/Dashboard.tsx (modified)
- Tests added: none required (npm run build passed)
- Context & Reference files read:
  - frontend/src/pages/Dashboard.tsx
  - frontend/src/components/SankeyChart.tsx
  - conductor/ui-overhaul-plan.md
- Notes: none
