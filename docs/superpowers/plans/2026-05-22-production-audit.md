# Issue-115 Production Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Conduct a comprehensive audit of the production environment on Raspberry Pi and document the findings.

**Architecture:** SSH-based remote command execution and report generation.

**Tech Stack:** SSH, Docker Compose, Bash, Markdown.

---

### Task 1: Check Container Status

**Files:**
- Output: Temporary logs (stdout)

- [ ] **Step 1: Execute SSH command to check docker compose ps**

Run: `ssh pi-r410 "cd ~/kakeibo-ai && docker compose ps"`
Expected: List of running containers (backend, frontend, slack, etc.) with status "Up".

### Task 2: Inspect Logs for Errors

**Files:**
- Output: Temporary logs (stdout)

- [ ] **Step 1: Execute SSH command to fetch backend and slack logs**

Run: `ssh pi-r410 "cd ~/kakeibo-ai && docker compose logs --tail=100 backend slack"`
Expected: Log output. Look for stack traces, "empty result" messages from Gemini API, or connection errors.

### Task 3: Verify Configuration Files

**Files:**
- Output: Temporary content (stdout)

- [ ] **Step 1: Read production .env file**

Run: `ssh pi-r410 "cd ~/kakeibo-ai && cat prod_local/.env"`
Expected: Verify `GEMINI_API_KEY`, `LLM_PROVIDER`, `KAKEIBO_LOCAL_DIR`.

- [ ] **Step 2: Read production settings.json file**

Run: `ssh pi-r410 "cd ~/kakeibo-ai && cat prod_local/config/settings.json"`
Expected: Verify `active_model`.

### Task 4: Check System Resources

**Files:**
- Output: Temporary status (stdout)

- [ ] **Step 1: Check disk space and memory usage**

Run: `ssh pi-r410 "df -h && free -m"`
Expected: Disk usage below 90%, available memory > 100MB.

### Task 5: Generate Audit Report

**Files:**
- Create: `docs/production_audit_report_20260522.md`

- [ ] **Step 1: Consolidate all findings into a Markdown report**

Create the file with the following structure:
- Summary
- Container Status
- Log Analysis (highlighting any issues)
- Configuration Check
- Resource Usage
- Recommendations / Next Steps
