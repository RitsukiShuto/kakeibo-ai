# Plan: @data-analyst プロンプト改善と分析ロジックの刷新

## Objective
@data-analyst のプロンプトを「役割（システム）」「口調（ペルソナ）」「構造（出力形式）」に分離し、Python側での事前集計（プリ・プロセッシング）を導入することで、分析精度とメンテナンス性を向上させる。

## Acceptance Criteria
- [ ] プロンプトが `system_prompt.md`, `personas/*.md`, `output_structure.md` に適切に分離されていること。
- [ ] `src/analyzer/gemini_analyzer.py` からハードコードされた「ギャル風に」等の指示が排除されていること。
- [ ] LLMに渡されるデータに、Python側で計算したカテゴリ別合計や予算消化率などの統計情報が含まれていること。
- [ ] 異なるペルソナ（執事、禅師、ギャル）を選択した際、それぞれの口調で適切な分析結果が得られること。
- [ ] `python tools/cli.py qa regression` がパスすること。

## Bootstrap (Developer loads this BEFORE writing any code)

### Skills to load
- `mini-sdd` — プロンプト設計とリファクタリングの指針。

## Confirmed Feature Behavior
- **Inputs:** 既存の家計明細、資産状況、予算、プロフィールデータ。
- **Outputs:** 各ペルソナに最適化された分析レポート（JSON形式）。
- **Edge cases handled:** ペルソナファイルが存在しない場合のデフォルト対応、給与未着時の予算ベース分析。
- **Out of scope:** 新しい分析指標の追加（今回は構造改善に注力）、UIの変更。

## Technical Design
### Approach
1. **プロンプトの外部化**: JSONスキーマと出力指示を `prompts/output_structure.md` に集約。
2. **統計計算の実装**: `gemini_analyzer.py` 内で、明細データからカテゴリ別集計、トップ支出、予算消化率などを算出するメソッドを追加。
3. **プロンプト結合ロジックの刷新**: ペルソナ + システム + 特別指示 + 構造定義 を順に結合するクリーンなロジックに変更。
4. **Few-shotの追加**: 日本の生活習慣（コンビニ、Amazon等）に合わせた分析例をシステムプロンプトに統合。

### Patterns & Conventions honored
- プロンプトの外部ファイル管理（既存パターン）。
- `KakeiboAnalyzer` 基底クラスの継承構造。

### Reference Files (Gold Standards — confirmed by user)
- `src/analyzer/gemini_analyzer.py` — 修正対象のメインロジック。
- `prompts/system_prompt.md` — 修正対象の基本プロンプト。

### Reused (do NOT recreate)
- `LLMFactory` — プロバイダー生成。
- `AIResponse` — 出力モデル。

## Tasks
1. [ ] **プロンプトファイルの再編**:
   - `prompts/output_structure.md` を作成し、JSONスキーマを移動。
   - `prompts/system_prompt.md` から特定の口調指示やフォーマット指示（出力形式と重複するもの）を削除。
   - `prompts/personas/*.md` を口調・アイデンティティのみに純粋化。
2. [ ] **統計計算ロジックの実装**:
   - `src/analyzer/gemini_analyzer.py` に `_calculate_statistics` メソッドを実装。
   - カテゴリ別合計、予算消化率、異常値（高額支出）の抽出を行う。
3. [ ] **分析メインロジックの修正**:
   - `analyze_kakeibo` を刷新。新プロンプト構成と計算済み統計量を使用するように変更。
   - ハードコードされた指示を排除し、完全な動的生成に移行。
4. [ ] **バリデーションとテスト**:
   - ダミーデータを用いた各ペルソナの動作確認。
   - 回帰テストの実行。

## Assumptions & Blind Spots

### Confirmed with user
- ペルソナとロジックを分離すること。
- Python側で集計してからLLMに渡すこと。

### Inferred from codebase (verified by reading)
- `AIResponse` モデルには既に `budget_status` や `asset_breakdown` が含まれているが、現在はLLMがこれらを計算している。

### Unverified assumptions (RISK — Developer must confirm first)
- 明細数が極端に多い場合（100件超）のコンテキスト上限への影響。集計データのみを渡すか、明細をどこまで絞るかの検討が必要。
