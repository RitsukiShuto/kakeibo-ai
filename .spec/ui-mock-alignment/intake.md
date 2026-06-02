2# Intake: UI Overhaul Mock Alignment Fix

## PR target branch
staging

## Raw prompt
UIの改修について、モックを再現できていません。 修正をお願いします。

## Clarifications (Q&A)
### Q1 — Mock Reference: 「再現できていないモック」とは、具体的にどのファイルを指していますか？
**Recommended:** docs/archive/dashboard_prototype/index.html
**User answered:** ~/tmp/mockup/index.html (Likely equivalent to docs/archive/dashboard_prototype/index.html in the workspace)

### Q2 — UI Direction: デザインの方向性について、どちらを優先すべきでしょうか？
**Recommended:** デザイン仕様書の通りカードを廃止しつつ、プロトタイプの配色や質感（Glassmorphism）を適用する
**User answered:** 事前に設計した通りの内容とする (Refers to conductor/ui-overhaul-plan.md)

## Confirmed feature behavior
- **Theme:** Strict Dark Theme (Slate-950 background) as described in the plan.
- **Layout:** Abolish traditional "cards" with thick borders/backgrounds, moving towards a "flowing document" style with sections separated by whitespace and large typography.
- **KPIs:** Large font "StatItem" components.
- **Features:** Must include the new components like SankeyChart, BudgetPacemaker, and AI Insights.
- **Responsive:** Must maintain the layout structure for large screens (main-content with fixed sidebar).

## Reference Files (confirmed by user)
- conductor/ui-overhaul-plan.md — Gold Standard for Feature set and Structure.
- docs/archive/dashboard_prototype/index.html — Reference for aesthetic quality and spacing.
- frontend/src/index.css — Contains the correct CSS tokens (Vibrant Minimalist) that must be used.

## Architecture constraints (confirmed)
- React with Tailwind CSS.
- **CRITICAL:** Use CSS variables from index.css instead of hardcoding light-mode slate colors.
- Component-based structure for Dashboard.

## Reuse (do NOT recreate)
- frontend/src/components/SankeyChart.tsx — Existing Sankey implementation.
- frontend/src/components/BudgetPacemaker.tsx — Existing pacemaker logic (needs styling fix).
- frontend/src/components/BudgetForm.tsx — Existing form implementation (needs styling fix).

## Unverified assumptions (RISK)
- The user might still want some "glassmorphism" effects which technically use backgrounds, even if "cards" are abolished. We will use the `.glass` utility where appropriate for subtle sectioning.
