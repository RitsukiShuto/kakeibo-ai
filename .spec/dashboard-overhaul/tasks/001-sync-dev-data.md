# 001 — Implement DEV data synchronization tool

## Context files (read for understanding — do not modify)
- tools/ops/sync_prod_to_staging.py — existing sync logic to replicate for dev.
- AGENTS.md — environment separation rules (development in dev_local/).

## Reference files (STRICT STYLE MATCH)
- tools/ops/sync_prod_to_staging.py — imitate the anonymization and safety guards.

## Required Skills
- List any skills from scope.md that should be loaded for this task (none).

## Files to create/modify (suggested)
- tools/ops/sync_prod_to_dev.py — create (tool to sync prod data to local/kakeibo.db)

## Description
Create a new tool `tools/ops/sync_prod_to_dev.py` that synchronizes production data to the local development environment (`local/kakeibo.db`). 
- Replicate logic from `sync_prod_to_staging.py`.
- Ensure strict anonymization of `comment`, `content` (if exists), and `institution` names.
- The destination must be `local/kakeibo.db`.
- Add a safety check to ensure it doesn't overwrite if not in a dev environment.
- Run the tool once after creation to populate the dev database for verification of subsequent tasks.

## Acceptance
- [ ] `tools/ops/sync_prod_to_dev.py` exists and is executable.
- [ ] Running the script successfully populates `local/kakeibo.db` with anonymized data.
- [ ] Transaction comments in the dev DB show "Store [Category]" instead of real names.

## Needs tests
no (tool-based manual verification)

---

## Implementation log (filled by dev after successful commit)
- Commit: b93663f7fea0d795f5acb1670bc26c0d582fa5a9 — feat(dashboard-overhaul): add dev data synchronization tool
- Files modified:
  - tools/ops/sync_prod_to_dev.py (created)
- Tests added: none required (tool-based manual verification)
- Context & Reference files read:
  - tools/ops/sync_prod_to_staging.py
  - AGENTS.md
- Notes: none
