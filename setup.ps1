# Kakeibo AI Review System セットアップスクリプト
$EnvName = "kakeibo-ai"

Write-Host "=== kakeibo_AI_ReviewSys セットアップを開始します ===" -ForegroundColor Cyan

# 1. Conda環境の確認と作成
Write-Host "`n[1/4] Anaconda環境を構築しています..." -ForegroundColor Yellow
$envs = conda env list | Out-String
if ($envs -match $EnvName) {
    Write-Host "環境 '$EnvName' は既に存在します。更新を確認します。"
    conda env update -n $EnvName -f environment.yml
} else {
    conda env create -f environment.yml
}

# 2. Playwrightのブラウザインストール
Write-Host "`n[2/4] Playwrightのブラウザをインストールしています..." -ForegroundColor Yellow
conda run -n $EnvName playwright install chromium

# 3. 環境設定ファイルの準備
Write-Host "`n[3/4] 環境設定ファイルを準備しています..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host ".env ファイルを作成しました。必要なAPIキーを設定してください。" -ForegroundColor Green
} else {
    Write-Host ".env ファイルは既に存在します。スキップします。"
}

# 4. ディレクトリの作成
Write-Host "`n[4/4] 必要なディレクトリを作成しています..." -ForegroundColor Yellow
$dirs = @("data", "logs", "reports/Reviews/Kakeibo")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "Created: $dir"
    }
}

Write-Host "`n=== セットアップが完了しました！ ===" -ForegroundColor Cyan
Write-Host "1. '.env' ファイルを開き、GEMINI_API_KEY などを設定してください。"
Write-Host "2. 'powershell ./run.ps1 --no-headless' を実行して、MoneyForwardにログインしてください。"
