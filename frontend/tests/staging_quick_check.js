import { chromium } from '@playwright/test';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  const targetUrl = 'http://192.168.0.21:5174/';
  console.log(`Connecting to ${targetUrl}...`);
  
  try {
    await page.goto(targetUrl, { waitUntil: 'networkidle', timeout: 30000 });
    
    const title = await page.title();
    console.log(`Page Title: ${title}`);
    
    // Check for some text that should be in the dashboard
    const content = await page.content();
    const hasKakeibo = content.includes('Kakeibo');
    const hasAssets = content.includes('資産') || content.includes('Assets');
    
    console.log(`Contains 'Kakeibo': ${hasKakeibo}`);
    console.log(`Contains 'Assets/資産': ${hasAssets}`);
    
    // Check for KPI cards
    const kpiCount = await page.locator('.kpi-card').count();
    console.log(`Number of KPI cards found: ${kpiCount}`);
    
    if (kpiCount > 0) {
      console.log('✅ Staging environment is accessible and rendering correctly.');
    } else {
      console.log('⚠️ Page loaded but KPI cards not found. Is the backend running?');
    }

  } catch (error) {
    console.error(`❌ Failed to connect to staging environment: ${error.message}`);
  } finally {
    await browser.close();
  }
})();
