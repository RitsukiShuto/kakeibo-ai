# Intake: Dashboard Layout Fix

## PR target branch
staging

## Raw prompt
改修したダッシュボードでレイアウト崩れが発生しているので修正してください

## Clarifications (Q&A)
### Q1 — Layout Issue: 「レイアウト崩れ」の具体的な内容はどのようなものですか？
**Recommended:** Visual/Structural Bug (要素の重なり、文字の見えにくさ、グリッドの崩れなど)
**User answered:** Visual/Structural Bug

### Q2 — Design Standard: デザインの正解（ゴール）はどちらに近いですか？
**Recommended:** Current Dashboard.tsx (現在の構成を維持)
**User answered:** Current Dashboard.tsx

### Q3 — CSS Approach: 今後の修正方針としてどちらを優先すべきですか？
**Recommended:** Established CSS Classes (index.css に定義された共通クラスを活用)
**User answered:** Established CSS Classes

## Confirmed feature behavior
- **Objective:** Fix the layout collapse and visual bugs in the current `Dashboard.tsx` while maintaining its general structure.
- **Key Fixes:**
    - Fix invisible text (e.g., `text-slate-900` used in `StatItem` and `ProgressBar` on dark background).
    - Fix high-contrast/legacy light theme elements (e.g., `bg-slate-100`, `border-slate-100` in `BudgetPacemaker` and `ProgressBar`).
    - Align the component styles with the global theme tokens and classes defined in `index.css` (e.g., using `.card`, `.kpi-card`, `.dashboard-grid` where appropriate, or at least using the CSS variables).
    - Ensure responsive behavior works correctly.

## Reference Files (confirmed by user)
- `frontend/src/index.css` — Gold Standard for theme tokens, global classes (`.card`, `.main-content`), and CSS variables.
- `frontend/src/pages/Dashboard.tsx` — The file to be fixed.
- `docs/archive/dashboard_prototype/index.html` — Reference for spacing and general aesthetic intent, although the current component structure is prioritized.

## Architecture constraints (confirmed)
- Maintain the current React component structure in `Dashboard.tsx`.
- Prioritize CSS classes from `index.css` over raw Tailwind utilities where they overlap.
- Ensure compatibility with the global dark theme.

## Reuse (do NOT recreate)
- Use CSS variables defined in `:root` of `index.css` (e.g., `var(--text-main)`, `var(--border)`, `var(--card-bg)`).

## Unverified assumptions (RISK)
- None at this stage.
