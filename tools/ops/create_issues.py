import subprocess
import sys

issues = [
    {
        "title": "[Stability] actions-runnerの常駐化と自動復旧の確認",
        "body": "Raspberry Piの再起動時にランナーが自動起動することをテストする。また、`svc.sh` 経由でのサービス登録をドキュメント化し、パス変更時の対処法（uninstall/install）を整備する。",
        "label": "maintenance"
    },
    {
        "title": "[Bug] グラフ生成時の日本語文字化け警告の修正",
        "body": "test_visualizer.py 実行時に発生する `UserWarning: Glyph ... missing from font(s) Arial` を解消するため、日本語対応フォントを指定し、警告を抑制するロジックを導入する。",
        "label": "bug"
    },
    {
        "title": "[Feature] ギャル・フィードバック・ループの実装",
        "body": "Slackの「やったよ」ボタンの入力をDBに記録し、次回のAI分析時に「前回のアクションの達成状況」としてプロンプトに組み込むことで、継続的な改善を促す仕組みを作る。",
        "label": "enhancement"
    },
    {
        "title": "[DX] 開発環境のDocker化",
        "body": "PlaywrightやMinicondaのセットアップをDocker Composeにまとめ、`docker-compose up` で開発環境が即座に立ち上がるようにする。Raspberry Pi上での実行もコンテナ化を検討する。",
        "label": "dx"
    },
    {
        "title": "[Feature] 異常支出のリアルタイム検知アラート",
        "body": "デイリー分析時に、過去の平均から大きく外れる高額決済（例: 3万円以上の買い物）があった場合、Slackに緊急通知する機能を追加する。",
        "label": "enhancement"
    }
]

def create_issue(title, body, label):
    cmd = [
        "gh", "issue", "create",
        "--title", title,
        "--body", body,
        "--label", label
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Success: {title}")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {title}")
        print(e.stderr)

def main():
    print("🚀 Creating recommended issues for Kakeibo AI...")
    for issue in issues:
        create_issue(issue["title"], issue["body"], issue["label"])

if __name__ == "__main__":
    main()
