# Kakeibo AI Review System Setup Script
# ルートディレクトリに移動
Set-Location "$PSScriptRoot\.."

$EnvName = "kakeibo-ai"

Write-Host "=== kakeibo_AI_ReviewSys Setup Start ===" -ForegroundColor Cyan

# 1. Conda Environment
Write-Host "`n[1/4] Checking Conda environment..." -ForegroundColor Yellow
$envs = conda env list | Out-String
if ($envs -match $EnvName) 
{
    Write-Host "Environment '$EnvName' already exists. Updating..."
    conda env update -n $EnvName -f environment.yml
} 
else 
{
    conda env create -f environment.yml
}

# 2. Playwright
Write-Host "`n[2/4] Installing Playwright browsers..." -ForegroundColor Yellow
conda run -n $EnvName playwright install chromium

# 3. Environment File
Write-Host "`n[3/4] Preparing .env file..." -ForegroundColor Yellow
if (-not (Test-Path "local")) { New-Item -ItemType Directory -Path "local" | Out-Null }
if (-not (Test-Path "local/.env")) 
{
    Copy-Item "local/.env.example" "local/.env"
    Write-Host "local/.env file created. Please set your API keys." -ForegroundColor Green
} 
else 
{
    Write-Host "local/.env file already exists. Skipping."
}

# 4. Directories
Write-Host "`n[4/4] Creating directories..." -ForegroundColor Yellow
$dirs = @("local/config", "data", "logs", "reports/Reviews/Kakeibo", "data/import/transactions")
foreach ($dir in $dirs) 
{
    if (-not (Test-Path $dir)) 
    {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "Created: $dir"
    }
}

# Copy initial config files from local/config/*.example
Get-ChildItem "local/config/*.json.example" | ForEach-Object {
    $dest = $_.FullName.Replace(".example", "")
    if (-not (Test-Path $dest)) {
        Copy-Item $_.FullName $dest
    }
}
Write-Host "Directories prepared and initial config files created in local/config/."

Write-Host "`n=== Setup Completed! ===" -ForegroundColor Cyan
Write-Host "1. Edit 'local/.env' and set GEMINI_API_KEY, etc."
Write-Host "2. Run 'powershell ./scripts/run.ps1 --no-headless' to login to MoneyForward."
Write-Host "3. If you have historical CSVs, put them in 'data/import/transactions' and run:"
Write-Host "   conda run -n $EnvName python tools/cli.py import mf-csv [CSV_PATH]" -ForegroundColor Gray
