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

完了後、設定を反映させます：
```bash
source ~/.bashrc
```

## 4. 環境設定 (.env)
PC側で作成済みの `.env` を転送するか、新規作成してください。

```bash
# PC(PowerShell)から転送する場合の例
scp .env [ユーザー名]@[IPアドレス]:~/kakeibo-ai/
```

## 5. ログインセッションの転送 (重要)
Raspberry Pi (SSH) 環境ではブラウザでの初回ログイン（2段階認証）が困難です。PC側で一度ログインを済ませたセッション情報を丸ごと転送します。

```bash
# PC(PowerShell)からの転送例
scp -r ./mf_session [ユーザー名]@[IPアドレス]:~/kakeibo-ai/
```

## 6. 動作確認
まずはデバッグモード（Slack/Obsidian連携オフ）で、コンソールにレポートが表示されるか確認します。

```bash
conda activate kakeibo-ai
python main.py --source mf --timeframe weekly --no-slack --no-obsidian
```

## 7. 定期実行の設定 (Cron)
毎週月曜の朝9時に実行する場合の設定例です。

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
- **メモリ不足**: Raspberry Pi 4 (2GB以下) の場合、ブラウザ実行中にスワップメモリを増やす必要があるかもしれません。
