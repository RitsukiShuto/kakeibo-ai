# 002 — Refine Budget and Sankey backend logic

## Context files (read for understanding — do not modify)
- src/api/utils.py — load_budget and category total logic.
- src/api/routers/dashboard.py — current Sankey flow logic.
- src/api/routers/analysis.py — current weekly win/loss logic.

## Reference files (STRICT STYLE MATCH)
- src/api/routers/dashboard.py — maintain the pattern for data aggregation and response format.

## Required Skills
- List any skills from scope.md that should be loaded for this task (none).

## Files to create/modify (suggested)
- src/api/routers/analysis.py — modify `get_weekly_form` to filter for variable expenses.
- src/api/routers/dashboard.py — modify `get_stats_flow` to map generic income sources.

## Description
Update backend logic to meet budget and Sankey requirements:
1. In `src/api/routers/analysis.py`, update `get_weekly_form` so that `weekly_budget` and `actual` transactions only include categories listed under `variable` (やりくり費) in the budget config.
2. In `src/api/routers/dashboard.py`, update `get_stats_flow` to map income sources. If `source` is "Moneyforward" (or other generic aggregator), use the `category` or `genre` to label it as "Salary", "Savings", "Investment", or "Other Income" in the Sankey nodes.

## Acceptance
- [ ] `get_weekly_form` API response reflects win/loss based only on variable expenses.
- [ ] `get_stats_flow` API response shows specific income labels (Salary, etc.) instead of generic aggregator names.
- [ ] Backend tests for these endpoints pass.

## Needs tests
yes | tool = pytest, location = tests/test_api.py or new tests/test_dashboard_refinement.py

---

## Implementation log (filled by dev after successful commit)
- Commit: 22d5288 — feat(dashboard-overhaul): refine budget win/loss and sankey income mapping
- Files modified:
  - src/api/routers/analysis.py (modified)
  - src/api/routers/dashboard.py (modified)
- Tests added: 2 (pytest)
- Notes: logic updated to filter for variable expenses only; income mapping for Moneyforward added.
