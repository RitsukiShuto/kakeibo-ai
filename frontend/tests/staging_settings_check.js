import { chromium } from '@playwright/test';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  const baseUrl = 'http://192.168.0.21:5174';
  const settingsUrl = `${baseUrl}/settings`;
  
  console.log(`Navigating to ${settingsUrl}...`);
  
  try {
    const response = await page.goto(settingsUrl, { waitUntil: 'networkidle', timeout: 30000 });
    console.log(`Response Status: ${response.status()}`);
    
    const title = await page.title();
    console.log(`Page Title: ${title}`);
    
    const content = await page.content();
    const hasSettings = content.includes('設定') || content.includes('Settings');
    console.log(`Contains 'Settings/設定': ${hasSettings}`);
    
    // Check for any console errors
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    page.on('pageerror', err => console.log('PAGE ERROR:', err.message));

    // Wait a bit to see if content renders
    await page.waitForTimeout(5000);
    
    const bodyText = await page.innerText('body');
    console.log('Body Text (first 200 chars):', bodyText.substring(0, 200));

    // Check if the sidebar is visible
    const sidebarVisible = await page.locator('nav').isVisible();
    console.log(`Sidebar Visible: ${sidebarVisible}`);

  } catch (error) {
    console.error(`❌ Error accessing /settings: ${error.message}`);
  } finally {
    await browser.close();
  }
})();
