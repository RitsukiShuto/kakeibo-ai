import { test, expect } from '@playwright/test';

test.describe('Kakeibo AI Dashboard E2E', () => {
  test.beforeEach(async ({ page }) => {
    // フロントエンドにアクセス
    await page.goto('http://localhost:5173');
    // APIの読み込み待ち（データが表示されるまで少し待つ）
    await page.waitForTimeout(2000);
  });

  test('Dashboard shows KPI and charts', async ({ page }) => {
    // KPIカードの存在確認
    await expect(page.locator('.kpi-card')).toHaveCount(4);
    
    // 特定のKPIタイトルが含まれているか
    await expect(page.getByText('実支出 (Actual)')).toBeVisible();
    await expect(page.getByText('総資産 (Total Assets)')).toBeVisible();

    // グラフタイトルの確認
    await expect(page.getByText('予実管理 (カテゴリ別)')).toBeVisible();
    await expect(page.getByText('資産推移')).toBeVisible();
  });

  test('Transactions page allows search and edit', async ({ page }) => {
    // 明細一覧ページへ移動
    await page.click('text=明細一覧');
    await expect(page).toHaveURL(/.*transactions/);

    // 検索入力の確認
    const searchInput = page.getByPlaceholder('明細を検索 (摘要やカテゴリ)...');
    await expect(searchInput).toBeVisible();
    
    // テーブルまたは「明細が見つかりません」のメッセージが表示されているか
    await expect(page.locator('.transaction-table').or(page.getByText('明細が見つかりません'))).toBeVisible();

    // データがある場合のみ編集テストを行う
    const editButton = page.locator('.btn-outline').first();
    if (await editButton.isVisible()) {
      await editButton.click();
      // 保存ボタンが表示されるか
      await expect(page.locator('.btn-success')).toBeVisible();
      // キャンセル
      await page.click('text=キャンセル');
    }
  });

  test('Expense Splitter page shows pending items', async ({ page }) => {
    // 立替・精算ページへ移動
    await page.click('text=立替・精算');
    await expect(page).toHaveURL(/.*expense-splitter/);

    // セクションタイトルの確認
    await expect(page.getByText('精算待ちリスト')).toBeVisible();
    await expect(page.getByText('これ立替？ (AI Detection)')).toBeVisible();

    // AI判定ボタンの存在確認 (Strict mode回避のため role 指定)
    await expect(page.getByRole('button', { name: 'AIに判定させる' })).toBeVisible();
  });

  test('AI Review page shows history', async ({ page }) => {
    // AIレビューページへ移動
    await page.click('text=AIレビュー');
    await expect(page).toHaveURL(/.*ai-review/);

    // 履歴リストの存在確認
    await expect(page.locator('.history-list')).toBeVisible();
  });

  test('Settings page shows JSON editors', async ({ page }) => {
    // 設定ページへ移動
    await page.click('text=設定');
    await expect(page).toHaveURL(/.*settings/);

    // テキストエリア（JSONエディタ）の存在確認
    await expect(page.locator('textarea')).toHaveCount(2);
    await expect(page.getByText('予算設定 (budget.json)')).toBeVisible();
  });
});
