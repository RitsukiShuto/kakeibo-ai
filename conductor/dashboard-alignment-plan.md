# Dashboard Overhaul Alignment Plan

## Objective
The current dashboard implementation deviates from the predefined "Vibrant Minimalist" design specified in `conductor/ui-overhaul-plan.md`. The goal of this plan is to correct the layout, typography, and component structures to strictly align with the design specifications.

## Key Changes
1. **Abolish Card Containers**: Remove legacy `.card` and `.kpi-card` wrappers to establish a "flowing document" layout defined by whitespace and typography rather than borders and background colors.
2. **Overview Typography**: Significantly increase the font size of key metrics (Total Expense, Daily Average, Score) to create a strong visual hierarchy.
3. **High-Density Layout**: Reposition the Asset Pie Chart and integrate it seamlessly into the Overview section. Transform the Recent Transactions and Reimbursements sections into minimal, high-density lists.
4. **AI Insights & Cash Flow**: Simplify AI Insights to plain text without backgrounds. Optimize the Sankey chart for a full-width, high-density display.
5. **Operations (Weekly Form)**: Integrate the win/loss/draw "Weekly Form" into the Budget Pacemaker section to provide immediate visual feedback on spending pace.

## Testing and Verification
- **Frontend Tests**: Update `Dashboard.test.tsx` and `ProgressBar.test.tsx` to align with the new structural changes, updated labels, and semantic CSS classes, ensuring all 16 frontend tests pass.
- **Backend Tests**: Verify that the 64 backend tests remain unaffected by the frontend changes.
- **Build**: Ensure `npm run build` completes without errors or unused imports.