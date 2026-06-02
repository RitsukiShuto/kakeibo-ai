# 004 — Recent Transactions & Reimbursements

## Context files (read for understanding — do not modify)
- frontend/src/pages/Dashboard.tsx — Current implemented sections.

## Reference files (STRICT STYLE MATCH)
- conductor/ui-overhaul-plan.md — Description of "Operations (直近の明細)" and "Reimbursements".

## Required Skills
- none

## Files to create/modify (suggested)
- frontend/src/pages/Dashboard.tsx — modify (overhaul Transactions and Reimbursements sections)

## Description
Overhaul the **Recent Transactions** and **Reimbursements** sections in `Dashboard.tsx`:
- Transactions: Display as a high-density list with minimal information (Date, Category, Amount). Remove the table structure if a flex-based list is more document-like and high-density.
- Reimbursements: Position the "pending reimbursements" list and "AI stand-in detection" in a balanced layout at the bottom of the dashboard.
- Ensure all sections follow the "Vibrant Minimalist" aesthetic without contained card backgrounds.

## Acceptance
- [ ] Recent Transactions are displayed in a high-density format.
- [ ] Reimbursements section is integrated at the bottom with a clean layout.
- [ ] All borders and backgrounds from legacy cards are removed.

## Needs tests
yes | tool = npm run build (frontend), location = frontend/

## Implementation log (filled by dev after successful commit)
- Commit: 3f07103 — feat(dashboard-overhaul-alignment): overhaul recent transactions and reimbursements
- Files modified:
  - frontend/src/pages/Dashboard.tsx (modified)
- Tests added: none required (npm run build passed)
- Context & Reference files read:
  - frontend/src/pages/Dashboard.tsx
  - .spec/dashboard-overhaul-alignment/design.md
  - conductor/ui-overhaul-plan.md
- Notes:
  - Rearranged the Dashboard structure to align with `ui-overhaul-plan.md`: AI Insights (Full width) -> Cash Flow (Full width) -> Operations (Budget + Recent Transactions) -> Reimbursements (Bottom).
  - Overhauled Recent Transactions into a high-density flex-based list with minimal information (Date, Category, Amount).
  - Overhauled Reimbursements section into a balanced two-column layout showing pending items and AI detection suggestions.
  - Integrated `/api/expense-splitter/detect` (POST) to fetch AI suggestions.
  - Removed all card-based backgrounds and borders to achieve the "Vibrant Minimalist" flowing document aesthetic.
