import typer
import sys
import os
from typing import Optional

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

app = typer.Typer(help="Kakeibo AI Unified CLI", no_args_is_help=True)

# --- DB Commands ---
db_app = typer.Typer(help="Database management tools", no_args_is_help=True)
app.add_typer(db_app, name="db")

@db_app.command(name="inspect")
def db_inspect():
    """Inspect the local database content."""
    from tools.db import inspect_db
    inspect_db.inspect_db()

@db_app.command(name="migrate")
def db_migrate():
    """Run database migrations."""
    from tools.db import migrate_reimbursement
    migrate_reimbursement.migrate()

# --- Fetch Commands ---
fetch_app = typer.Typer(help="Data fetching tools", no_args_is_help=True)
app.add_typer(fetch_app, name="fetch")

@fetch_app.command(name="history")
def fetch_history(
    months: int = typer.Option(12, help="Number of months to go back"),
    headless: bool = typer.Option(True, help="Run browser in headless mode")
):
    """Bulk fetch historical data from MoneyForward."""
    from tools.fetch import fetch_history
    fetch_history.fetch_history(months, headless)

@fetch_app.command(name="fast")
def fetch_fast(
    months: int = typer.Option(12, help="Number of months to go back"),
    headless: bool = typer.Option(True, help="Run browser in headless mode")
):
    """Fast fetch historical data using direct CSV download URLs."""
    from tools.fetch import fetch_history_fast
    fetch_history_fast.fetch_history_fast(months, headless)

@fetch_app.command(name="setup-session")
def fetch_setup_session(
    headless: bool = typer.Option(False, "--no-headless", help="Run browser in headless mode")
):
    """Setup MoneyForward session manually."""
    from tools.fetch import setup_mf_session
    setup_mf_session.main()

# --- Analysis Commands ---
analysis_app = typer.Typer(help="AI Analysis tools", no_args_is_help=True)
app.add_typer(analysis_app, name="analysis")

@analysis_app.command(name="run")
def analysis_run(
    timeframe: str = typer.Argument("monthly", help="Timeframe (daily, weekly, monthly, yearly)")
):
    """Run AI analysis on prepared input data."""
    from tools.analysis import run_analysis
    # Inject argument into sys.argv because run_analysis.main uses it
    sys.argv = [sys.argv[0], timeframe]
    run_analysis.main()

@analysis_app.command(name="prepare")
def analysis_prepare(
    days: int = typer.Option(30, help="Number of days to include"),
    output: str = typer.Option("input_data.json", help="Output file path")
):
    """Prepare input data for AI analysis."""
    from tools.analysis import prepare_input
    prepare_input.main()

@analysis_app.command(name="models")
def analysis_models():
    """List available AI models."""
    from tools.analysis import list_models
    list_models.main()

# --- Import Commands ---
import_app = typer.Typer(help="Data import tools", no_args_is_help=True)
app.add_typer(import_app, name="import")

@import_app.command(name="mf-csv")
def import_mf_csv(
    file_path: str = typer.Argument(..., help="Path to the MoneyForward CSV file"),
    db_path: Optional[str] = typer.Option(None, help="Path to the database file")
):
    """Import transactions from a MoneyForward CSV file."""
    from tools.import_data import import_mf_csv
    import_mf_csv.import_csv(file_path, db_path or "local/kakeibo.db")

# --- QA Commands ---
qa_app = typer.Typer(help="Quality assurance and testing tools", no_args_is_help=True)
app.add_typer(qa_app, name="qa")

@qa_app.command(name="regression")
def qa_regression(
    e2e: bool = typer.Option(False, "--e2e", help="Run E2E tests")
):
    """Run local full regression suite."""
    from tools.qa import run_regression
    if e2e:
        sys.argv.append("--e2e")
    run_regression.main()

@qa_app.command(name="test-gemini")
def qa_test_gemini():
    """Test Gemini API connectivity and basic functionality."""
    from tools.qa import test_gemini
    test_gemini.main()

@qa_app.command(name="test-slack")
def qa_test_slack():
    """Test Slack notification."""
    from tools.qa import test_slack
    test_slack.test_slack()

@qa_app.command(name="check-api")
def qa_check_api():
    """Check backend API health."""
    from tools.qa import check_api
    check_api.main()

# --- Ops Commands ---
ops_app = typer.Typer(help="Operational tools", no_args_is_help=True)
app.add_typer(ops_app, name="ops")

@ops_app.command(name="sync-staging")
def ops_sync_staging():
    """Sync production data to staging (Run on Pi)."""
    from tools.ops import sync_prod_to_staging
    sync_prod_to_staging.main()

if __name__ == "__main__":
    app()
