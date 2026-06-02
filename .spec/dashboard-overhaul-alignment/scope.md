# Scope: Dashboard Overhaul Alignment

## Objective
Align the dashboard implementation with the "Vibrant Minimalist Overhaul" design specified in `conductor/ui-overhaul-plan.md` to ensure a consistent, document-like, and high-density user experience.

## User stories
- As a user, I want the dashboard to follow the Vibrant Minimalist design so that I can focus on my financial insights without visual clutter.
- As a user, I want to see key metrics like Total Expense in large typography so that I can instantly understand my financial status.
- As a user, I want to see my budget pace and weekly performance so that I can adjust my spending in real-time.

## Acceptance criteria
- [ ] Dashboard is rendered using the "Vibrant Minimalist" philosophy, using whitespace and bold typography instead of borders/backgrounds for sectioning.
- [ ] All `.card` classes and associated borders/backgrounds are removed from dashboard sections.
- [ ] Overview section displays "Total Expense", "Daily Average", and "Kakeibo Score" with massive font sizes in a high-density horizontal layout.
- [ ] "Asset Composition (Pie Chart)" is positioned on the right side of the Overview section.
- [ ] AI Insights are displayed as pure plain text (approx. 2 lines) without any background or border.
- [ ] Cash Flow (Sankey Chart) is full-width, multi-layered, and has a height of approximately 450px.
- [ ] Budget Pacemaker progress bars include a "Pace Limit" (orange line) representing the ideal spending for the current day.
- [ ] Budget Pacemaker supports switching between Weekly, Monthly, Quarterly, and Yearly timeframes via a toggle.
- [ ] "Weekly Form" (W/L/D/ -) is integrated into the Operations section, with the current week highlighted by a vibrant border.
- [ ] Recent transactions are displayed as a high-density list with minimal information.
- [ ] The dashboard uses the Slate-950 base color with Indigo, Amber, and Emerald accents sourced from `index.css` variables.

## External Tools & Design Mocks
- Figma: none
- Other Tools: none

## Reference Files (Gold Standards)
- `conductor/ui-overhaul-plan.md` — The absolute Gold Standard for feature set and aesthetic direction.
- `frontend/src/index.css` — Standard for theme tokens and CSS variables.
- `frontend/src/pages/Dashboard.tsx` — Target for overhaul.

## Architecture constraints
- React, TypeScript, Tailwind CSS.
- No card-based containment.
- "Flowing document" document-first layout.

## Reuse (do NOT recreate)
- Existing sub-components (`AssetPieChart`, `SankeyChart`, `BudgetPacemaker`, `BudgetForm`) should be updated to fit the new layout rather than being replaced.

## Out of scope
- Implementation of Transactions, AI Review, or Settings page overhaul (this task is focused strictly on the Dashboard).
- Modification of backend logic unrelated to the dashboard's specific layout needs.
- Data migration or database schema changes.

## Unverified assumptions (RISK)
- none

## Context
The current dashboard implementation deviates from the approved "Vibrant Minimalist" design by relying on legacy card-based UI patterns. This task aims to correct those deviations by removing borders, increasing typography scale, and implementing the high-density document-like layout defined in the `ui-overhaul-plan.md`. This change is critical to elevating the user experience from simple management to intuitive insight.
