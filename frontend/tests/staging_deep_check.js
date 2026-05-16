import { chromium } from '@playwright/test';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  const targetUrl = 'http://192.168.0.21:5174/';
  console.log(`Deep-checking ${targetUrl}...`);
  
  // Capture console logs
  page.on('console', msg => console.log(`BROWSER LOG [${msg.type()}]: ${msg.text()}`));
  page.on('pageerror', err => console.log(`BROWSER ERROR: ${err.message}`));
  
  // Capture network requests
  page.on('request', request => {
    if (request.url().includes('/api/')) {
        console.log(`API REQUEST: ${request.method()} ${request.url()}`);
    }
  });
  page.on('response', response => {
    if (response.url().includes('/api/')) {
        console.log(`API RESPONSE: ${response.status()} ${response.url()}`);
    }
  });

  try {
    await page.goto(targetUrl, { waitUntil: 'networkidle', timeout: 30000 });
    
    // Wait for data loading
    await page.waitForTimeout(5000);
    
    const kpis = await page.locator('.kpi-card .value').allInnerTexts();
    console.log(`KPI Values: ${JSON.stringify(kpis)}`);
    
    const transactions = await page.locator('.pending-list li').allInnerTexts();
    console.log(`Recent Transactions count: ${transactions.length}`);

    // Try to click settings
    console.log('Attempting to click Settings...');
    const settingsButton = page.locator('nav a:has-text("設定"), nav a[href="/settings"]');
    if (await settingsButton.isVisible()) {
        await settingsButton.click();
        await page.waitForTimeout(3000);
        console.log(`URL after click: ${page.url()}`);
        console.log(`Page title after click: ${await page.title()}`);
        const content = await page.innerText('body');
        console.log(`Settings page body length: ${content.length}`);
    } else {
        console.log('Settings button not found in sidebar!');
        const navHtml = await page.locator('nav').innerHTML().catch(() => 'no nav found');
        console.log(`Nav HTML: ${navHtml}`);
    }

  } catch (error) {
    console.error(`❌ Error during deep check: ${error.message}`);
  } finally {
    await browser.close();
  }
})();
