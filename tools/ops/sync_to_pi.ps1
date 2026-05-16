# =================================================================
# Raspberry Pi Environment Sync Script (PowerShell Version)
# Transfers consolidated local directory to Raspberry Pi securely.
# =================================================================

# --- CONFIGURATION ---
$PI_USER = "r410"
$PI_HOST = "192.168.0.21"
$PI_DIR  = "~/kakeibo-ai"
# ---------------------

Write-Host "=== Syncing Local Directory to Raspberry Pi ===" -ForegroundColor Cyan

if (Test-Path "local")
{
    Write-Host "[1/1] Transferring local/ directory..."
    scp -r local "${PI_USER}@${PI_HOST}:${PI_DIR}/"
}
else
{
    Write-Host "Error: 'local' directory not found." -ForegroundColor Red
}

Write-Host "`n=== Sync Completed! ===" -ForegroundColor Cyan
Write-Host "Please check if 'python main.py' works on Raspberry Pi."
