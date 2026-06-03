# 004 — Overhaul Charts with Vivid Palette

## Context files (read for understanding — do not modify)
- frontend/src/components/AssetPieChart.tsx — current pie chart implementation.
- frontend/src/components/SankeyChart.tsx — current sankey chart implementation.

## Reference files (STRICT STYLE MATCH)
- frontend/src/components/AssetPieChart.tsx — maintain Recharts pattern.

## Required Skills
- List any skills from scope.md that should be loaded for this task (none).

## Files to create/modify (suggested)
- frontend/src/components/AssetPieChart.tsx — modify (Vivid palette)
- frontend/src/components/SankeyChart.tsx — modify (Vivid palette, custom node labels)

## Description
Apply vivid colors and improve chart readability:
1. Define a shared `VIVID_PALETTE` (e.g., `['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#82E0AA']`) and apply it to `AssetPieChart` and `SankeyChart`.
2. In `SankeyChart.tsx`, implement a custom `Node` component or custom `label` property to render both the node's name and its value (e.g., "Food: ¥12,345") statically on the chart. 
3. Ensure all text labels on the charts are white and clear against the vivid backgrounds.

## Acceptance
- [ ] Pie chart uses a more varied and high-contrast color set.
- [ ] Sankey chart shows names and amounts on each node without hovering.
- [ ] Chart labels are in white text and readable.

## Needs tests
no (UI manual verification)

---

## Implementation log (filled by dev after successful commit)
- Commit: 790b7f4 — feat(dashboard-overhaul): overhaul charts with vivid palette and static labels
- Files modified:
  - frontend/src/components/AssetPieChart.tsx (modified)
  - frontend/src/components/SankeyChart.tsx (modified)
  - frontend/src/utils/constants.ts (created)
- Tests added: none required (UI manual verification)
- Context & Reference files read:
  - frontend/src/components/AssetPieChart.tsx
  - frontend/src/components/SankeyChart.tsx
- Notes: Created a shared constants file for the vivid palette. Increased SankeyChart right margin to accommodate static labels.
