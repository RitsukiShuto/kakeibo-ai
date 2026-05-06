# 🍓 Raspberry Pi 構築ガイド (kakeibo_AI_ReviewSys)

本システムを Raspberry Pi で安定して稼働させるためのセットアップ手順です。

## ⚠️ 重要な注意事項
本システムで使用している **Playwright**（マネーフォワードのスクレイピング用）は、**Raspberry Pi OS 64-bit 版**を強く推奨します。32-bit 版では動作が非常に不安定、またはインストールに失敗する可能性があります。

- **推奨環境**: Raspberry Pi 4 以上 + Raspberry Pi OS (64-bit)

---

## 1. OSの準備 (64-bit化)
まだ OS が 32-bit の場合は、可能な限り 64-bit 版への再インストールを推奨します。
どうしても 32-bit のまま試す場合は、カーネルを 64-bit モードにする必要があります。

```bash
# カーネル 64-bit 化 (32-bit OSの場合のみ)
sudo nano /boot/config.txt
# 末尾に追記して再起動
arm_64bit=1
```

## 2. リポジトリの取得
```bash
git clone https://github.com/RitsukiShuto/kakeibo-ai.git
cd kakeibo-ai
```

## 3. 自動セットアップスクリプトの実行
Raspberry Pi 専用のセットアップスクリプトを実行します。これにより、Minicondaのインストール、仮想環境の構築、Playwrightの依存ライブラリ導入がすべて自動で行われます。

```bash
bash setup_raspberry_pi.sh
```

完了後, 設定を反映させます：
```bash
source ~/.bashrc
```

## 4. 環境設定とセッション情報の同期 (local/ フォルダ)
本システムでは、APIキー(`.env`)やブラウザのセッション情報(`mf_session`)、各設定ファイル(`local/config/*.json`)をすべて `local/` フォルダに集約しています。

PC側でセットアップが完了している場合、以下のスクリプト（または手動のscp）で Raspberry Pi へ一括転送できます。

```bash
# PC(Windows)の場合
powershell tools/sync_to_pi.ps1

# PC(Mac/Linux)の場合
bash tools/sync_to_pi.sh
```

手動で転送する場合は、`local/` フォルダごと転送してください：
```bash
scp -r local/ [ユーザー名]@[IPアドレス]:~/kakeibo-ai/
```

> **Note:** Raspberry Pi (SSH) 環境ではブラウザでの初回ログイン（2段階認証）が困難なため、PC側で一度ログインを済ませた `local/mf_session` を転送するのが最も簡単です。

## 5. 動作確認
まずはデバッグモード（Slack連携のみ、データ保存なし等）で、コンソールにレポートが表示されるか確認します。

```bash
conda activate kakeibo-ai
python main.py --source mf --timeframe weekly --no-obsidian
```

## 6. Slack 連携・ダッシュボードサーバーの常駐化
Slackから `/review` コマンドでいつでも分析を実行できるようにし、かつ Web ダッシュボードを常時閲覧可能にするため、Systemd でサービスを起動させます。

```bash
# サービスファイルのコピー
sudo cp infra/systemd/kakeibo-*.service /etc/systemd/system/
sudo cp infra/systemd/kakeibo-*.timer /etc/systemd/system/

# デーモンのリロードと有効化
sudo systemctl daemon-reload
sudo systemctl enable kakeibo-slack.service kakeibo-dashboard.service kakeibo-review.timer
sudo systemctl start kakeibo-slack.service kakeibo-dashboard.service kakeibo-review.timer
```


## 7. 定期実行の設定 (Cron)
毎週月曜の朝9時に自動実行する場合の設定例です。

```bash
crontab -e
```
末尾に追記：
```text
0 9 * * 1 cd ~/kakeibo-ai && /bin/bash run.sh --source mf
```

---

## 🛠 トラブルシューティング
- **Playwright エラー**: `playwright install-deps` が必要になる場合があります（スクリプト内で実行済みですが、失敗した場合は手動で実行してください）。
- **モジュールが見つからないエラー**: Cron で実行する際、`PYTHONPATH=.` の指定が必要な場合があります。
- **メモリ不足**: Raspberry Pi 4 (2GB以下) の場合、ブラウザ実行中にスワップメモリを増やす必要があるかもしれません。
