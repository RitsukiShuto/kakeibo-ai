# AI-Test Environment Setup Plan

This document outlines the setup and usage of the `ai-test` environment for the Kakeibo AI project. The `ai-test` environment is designed for evaluating prompt changes, model comparisons, and performing regression tests on AI-generated outputs without affecting development or production data.

## 1. Directory Structure

The `ai-test` environment uses a dedicated directory `ai_test_local/` at the project root. This follows the convention of `dev_local/` and `prod_local/`.

```
ai_test_local/
├── .env                  # Environment-specific variables
├── kakeibo.db           # Dedicated database for AI testing
├── config/              # Configuration files
│   ├── budget.json      # Test budget scenarios
│   ├── profile.json     # Test user profiles
│   ├── schedule.json    # Test execution schedule
│   └── settings.json    # AI settings (model, persona, etc.)
├── data/
│   └── import/          # Mock CSV data for import testing
└── reports/             # Storage for generated AI reports
```

## 2. Configuration

### Environment Variables (`ai_test_local/.env`)

The system uses `KAKEIBO_LOCAL_DIR` to determine the base directory for configuration and data.

```bash
# ai_test_local/.env
KAKEIBO_LOCAL_DIR=ai_test_local
LLM_PROVIDER=gemini
# Specific model for testing if supported by provider
# ACTIVE_MODEL=gemini-1.5-pro
```

### AI Settings (`ai_test_local/config/settings.json`)

Use this to switch personas or models specifically for testing.

```json
{
  "ai": {
    "active_persona": "gal",
    "active_model": "gemini-1.5-flash"
  }
}
```

## 3. Setup Process

To initialize the AI-Test environment, follow these steps:

1. **Create the directory structure**:
   ```bash
   mkdir -p ai_test_local/config
   mkdir -p ai_test_local/data/import
   ```

2. **Initialize configuration files**:
   Copy examples from `prod_local/config/` to `ai_test_local/config/`.

3. **Prepare test data**:
   Import sample transactions into `ai_test_local/kakeibo.db`.

   ```bash
   export KAKEIBO_LOCAL_DIR=ai_test_local
   python tools/cli.py import mf-csv path/to/test_data.csv
   ```

## 4. Execution

To run the AI analysis in the test environment:

```bash
# Set the environment variable and run
KAKEIBO_LOCAL_DIR=ai_test_local python main.py --skip-fetch --db-path ai_test_local/kakeibo.db
```

Using Docker:
Create a `docker-compose.ai-test.yml` that mounts `./ai_test_local` to `/app/local`.

```yaml
# docker-compose.ai-test.yml
services:
  backend:
    build: .
    volumes:
      - .:/app
      - ./ai_test_local:/app/local
    environment:
      - KAKEIBO_LOCAL_DIR=local
```

## 5. Required Code Changes

To fully support the `ai-test` environment (and other future environments), the following hardcoded paths must be updated to respect the `KAKEIBO_LOCAL_DIR` environment variable:

- **`src/analyzer/gemini_analyzer.py`**: Update `_get_active_persona()` to use `LOCAL_DIR`.
- **`src/analyzer/providers/factory.py`**: Update `create_provider()` to use `LOCAL_DIR` for `settings.json` path.
- **`src/output/slack_server.py`**: Update various handlers (`handle_chat_logic`, `handle_model_logic`, `handle_check`) to use `LOCAL_DIR` instead of the hardcoded `"local/config"`.

## 6. Implementation Steps

1. **Fix Hardcoded Paths**: Refactor the code as described above to ensure environmental consistency.
2. **Update `scripts/dev.sh`**: Add an `ai-test-setup` command to automate the creation of `ai_test_local`.
3. **CI/CD Integration**: Add a GitHub Action job that runs AI evaluations using this environment when prompts in `prompts/` are modified.

## 7. Verification Metrics

When running in `ai-test`, the following should be verified:
- JSON output validity (schema match).
- Consistency of "Totonoi Score".
- Persona adherence (tone and style).
- Accuracy of budget vs. actual calculations.
