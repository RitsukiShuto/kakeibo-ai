import { test, expect } from '@playwright/test';

test.describe('Kakeibo AI Dashboard E2E', () => {
  test.beforeEach(async ({ page }) => {
    // ダッシュボードを表示
    await page.goto('http://localhost:5173');
    // APIの読み込み待ち（簡易的な待機。本来はネットワークの終了を待つのがベター）
    await page.waitForTimeout(2000);
  });

  test('Dashboard shows KPI and charts', async ({ page }) => {
    // KPIカードが4枚表示されていること
    await expect(page.locator('.kpi-card')).toHaveCount(4);

    // 特定のKPIタイトルが含まれているか（日本語）
    await expect(page.getByText('実支出')).toBeVisible();
    await expect(page.getByText('総資産')).toBeVisible();

    // グラフタイトルの確認
    await expect(page.getByText('予実管理 (カテゴリ別)')).toBeVisible();
    await expect(page.getByText('資産推移')).toBeVisible();
  });

  test('Transactions page allows search and edit', async ({ page }) => {
    // 明細一覧ページへ遷移
    await page.click('text=明細一覧');
    await expect(page).toHaveURL(/.*transactions/);

    // 検索入力欄の確認
    const searchInput = page.getByPlaceholder('明細を検索 (内容、カテゴリ)...');
    await expect(searchInput).toBeVisible();

    // テーブルまたは空の状態メッセージが表示されていること
    await expect(page.locator('.transaction-table').or(page.getByText('明細データがありません'))).toBeVisible();

    // 編集ボタンの動作確認（モックデータがある場合）
    const editButton = page.locator('.btn-outline').first();
    if (await editButton.isVisible()) {
      await editButton.click();
      // 編集ダイアログ（またはフォーム）の表示確認
      await expect(page.locator('.btn-success')).toBeVisible();
      // キャンセル
      await page.click('text=キャンセル');
    }
  });

  test('Expense Splitter page shows pending items', async ({ page }) => {
    // 立替・精算ページへ遷移
    await page.click('text=立替・精算');
    await expect(page).toHaveURL(/.*expense-splitter/);

    // セクションタイトルの確認
    await expect(page.getByText('精算待ちの項目')).toBeVisible();
    await expect(page.getByText('立替金の自動検出 (AI Detection)')).toBeVisible();

    // AI抽出ボタンの確認
    await expect(page.getByRole('button', { name: 'AIで明細を解析する' })).toBeVisible();
  });

  test('AI Review page shows history', async ({ page }) => {
    // AIレビューページへ遷移
    await page.click('text=AIレビュー');
    await expect(page).toHaveURL(/.*ai-review/);

    // 履歴リストの表示確認
    await expect(page.locator('.history-list')).toBeVisible();
  });

  test('Settings page shows form and JSON editors', async ({ page }) => {
    // 設定ページへ遷移
    await page.click('text=設定');
    await expect(page).toHaveURL(/.*settings/);

    // デフォルトで「かんたん設定」が表示されているか
    await expect(page.getByText('AI モデル設定')).toBeVisible();
    await expect(page.getByText('プロフィール設定')).toBeVisible();

    // 「高度な設定 (JSON)」タブに切り替え
    await page.click('text=高度な設定 (JSON)');
    await expect(page.locator('textarea')).toHaveCount(2);
    await expect(page.getByText('budget.json')).toBeVisible();
  });
});
