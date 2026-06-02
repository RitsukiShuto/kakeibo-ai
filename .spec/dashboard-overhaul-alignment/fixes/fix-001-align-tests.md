# Fix 001 — Align Frontend Tests

## Description
Update frontend unit tests to align with the new English labels and semantic classes introduced by the "Vibrant Minimalist" overhaul.

## Implementation log
- **Commit**: fb45c491295982e0e0129a0f917540602f928e184
- **Files modified**: frontend/src/components/ProgressBar.tsx, frontend/src/components/__tests__/ProgressBar.test.tsx, frontend/src/test/Dashboard.test.tsx
- **Actions**: 
    - Mocked `client.post` in `Dashboard.test.tsx`.
    - Updated assertions to expect English labels ("Total Expense", "Cash Flow").
    - Restored semantic classes to `ProgressBar` and updated test assertions to match the new rendered output.
