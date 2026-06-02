# Intake: Dashboard Overhaul Alignment

## PR target branch
staging

## Raw prompt
事前に定めたデザイン通りになっていません。 原因を教えてください。

## Clarifications (Q&A)
### Q1 — Design Goal: 「事前に定めたデザイン」とは、具体的にどのドキュメントを指していますか？
**Recommended:** conductor/ui-overhaul-plan.md (Vibrant Minimalist Overhaul)
**User answered:** お願いします (Confirmed by context)

### Q2 — Identified Discrepancies: なぜ現在の実装がデザイン通りでないと判断しましたか？
**Recommended:** The previous implementation incorrectly used the legacy card-based prototype styles (.card) and lacked the "flowing document" style, large typography, and missing features like the "Weekly Form" in a high-density layout.
**User answered:** (Implicitly confirmed by accepting the root cause analysis)

## Confirmed feature behavior
- **Design Philosophy:** Vibrant Minimalist.
- **Abolish Cards:** Remove all `.card` classes and associated borders/backgrounds from dashboard sections. Use whitespace and bold typography for sectioning.
- **Overview Transformation:** 
    - Giant font sizes for "Total Expense", "Daily Average", and "Kakeibo Score".
    - High-density horizontal layout with "Asset Composition (Pie Chart)" on the right.
- **AI Insights:** Pure plain text summary (approx. 2 lines) with no background or border.
- **Cash Flow (Sankey):** Full-width, multi-layered flow with sufficient height (~450px).
- **Operations Section:**
    - High-density list display for recent transactions.
    - Integration of "Weekly Form" (W/L/D/ -) with highlighting for the current week.
    - Pace Limit (orange line) on progress bars.
- **Color Palette:** Slate-950 base with Indigo, Amber, and Emerald accents. Use CSS variables from `index.css`.

## Reference Files (confirmed by user)
- `conductor/ui-overhaul-plan.md` — The absolute Gold Standard for feature set and aesthetic direction.
- `frontend/src/index.css` — Standard for theme tokens and CSS variables.
- `frontend/src/pages/Dashboard.tsx` — Target for overhaul.

## Architecture constraints (confirmed)
- React, TypeScript, Tailwind CSS.
- No card-based containment.
- "Flowing document" document-first layout.

## Reuse (do NOT recreate)
- Existing sub-components (`AssetPieChart`, `SankeyChart`, `BudgetPacemaker`, `BudgetForm`) should be updated to fit the new layout rather than being replaced.

## Unverified assumptions (RISK)
- None.
