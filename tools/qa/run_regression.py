import subprocess
import sys
import os
import time
import shutil
from datetime import datetime

# カラー出力用の設定
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(message):
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}=== STEP: {message} ==={Colors.ENDC}")

def run_command(command, cwd=None, env=None, shell=True):
    """コマンドを実行し、成功か失敗かを返す"""
    print(f"Running: {command}")
    try:
        # Windows環境でのエンコーディング対応
        process = subprocess.run(
            command, 
            cwd=cwd, 
            env=env, 
            shell=shell, 
            check=True,
            text=True,
            capture_output=False
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.FAIL}Error executing command: {command}{Colors.ENDC}")
        return False

def main():
    start_time = time.time()
    results = {}
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    
    print(f"{Colors.HEADER}{Colors.BOLD}🚀 Kakeibo AI Local Full Regression Suite{Colors.ENDC}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. バックエンド単体・統合テスト
    print_step("Backend Unit & Integration Tests (pytest)")
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root
    env["KAKEIBO_CONFIG_DIR"] = "tests/config"
    results["Backend Tests"] = run_command(f"{sys.executable} -m pytest tests/ --ignore=tests/test_dashboard_e2e.py", cwd=project_root, env=env)

    # 2. フロントエンドビルドチェック
    print_step("Frontend Build & Type Check (npm run build)")
    frontend_dir = os.path.join(project_root, "frontend")
    if os.path.exists(frontend_dir):
        results["Frontend Build"] = run_command("npm run build", cwd=frontend_dir)
    else:
        print(f"{Colors.WARNING}Frontend directory not found, skipping.{Colors.ENDC}")

    # 3. E2Eテスト (任意実行または環境が整っている場合のみ)
    # ここでは、環境が整っていない場合の失敗を許容するか、明示的なフラグで制御するようにする
    if "--e2e" in sys.argv:
        print_step("E2E Tests (Playwright)")
        # 注意: E2Eを実行するには API と Frontend がバックグラウンドで動いている必要があります
        # 簡易化のため、ここではフラグがある場合のみ警告を出しつつ試行
        results["E2E Tests"] = run_command(f"{sys.executable} -m pytest tests/test_dashboard_e2e.py", cwd=project_root, env=env)

    # 結果のまとめ
    print(f"\n{Colors.BOLD}{Colors.HEADER}=== REGRESSION SUMMARY ==={Colors.ENDC}")
    all_passed = True
    for task, passed in results.items():
        status = f"{Colors.OKGREEN}PASS{Colors.ENDC}" if passed else f"{Colors.FAIL}FAIL{Colors.ENDC}"
        print(f"{task}: {status}")
        if not passed:
            all_passed = False

    duration = time.time() - start_time
    print(f"\nTotal Duration: {duration:.2f} seconds")

    if all_passed:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ ALL CHECKS PASSED. Ready to commit/merge!{Colors.ENDC}")
        sys.exit(0)
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ SOME CHECKS FAILED. Please fix them before merging.{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
