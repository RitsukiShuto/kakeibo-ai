# Kakeibo AI Review System 実行スクリプト
# ルートディレクトリに移動
Set-Location "$PSScriptRoot\.."
$EnvName = "kakeibo-ai"

Write-Host "=== Kakeibo AI Review System Task Started: $(Get-Date) ===" -ForegroundColor Cyan

# 引数を配列として取得
$passArgs = $args

# conda run を使用して実行
conda run -n $EnvName python main.py $passArgs

Write-Host "=== Task Completed: $(Get-Date) ===" -ForegroundColor Cyan
