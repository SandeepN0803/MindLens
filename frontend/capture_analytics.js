import puppeteer from 'puppeteer';
import path from 'path';

const outDir = 'C:\\Users\\sande\\.gemini\\antigravity\\brain\\4b2ff587-ec38-4d03-8fc2-69aa5da29df9';

async function run() {
  console.log("Launching browser...");
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  
  try {
    console.log("Navigating to app...");
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle0' });
    
    // Seed some data so charts aren't empty
    await page.evaluate(() => {
      window.localStorage.setItem('has_entries', 'true');
    });

    // Make window mobile
    await page.setViewport({ width: 375, height: 812, isMobile: true, hasTouch: true });
    
    // Write entry to get real data
    await page.waitForSelector('textarea', { timeout: 10000 });
    await page.type('textarea', 'I felt really overwhelmed at work today and thought I was going to get fired. It was terrible.');
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const analyzeBtn = buttons.find(b => b.textContent.includes('Analyze'));
      if (analyzeBtn) analyzeBtn.click();
    });

    console.log("Waiting for analysis...");
    await page.waitForFunction(() => {
      return document.body.innerText.includes('Analysis Overview');
    }, { timeout: 30000 });
    
    await new Promise(r => setTimeout(r, 1000));

    // Click Analytics tab (Mobile)
    console.log("Clicking Analytics tab...");
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('.md\\:hidden button'));
      const btn = buttons.find(b => b.textContent.includes('Analytics'));
      if (btn) btn.click();
    });
    
    // wait for charts to render
    await new Promise(r => setTimeout(r, 2000));
    
    // Take screenshot
    await page.screenshot({ path: path.join(outDir, 'mobile_analytics_final.png') });
    console.log("Captured mobile_analytics_final.png");

  } catch (error) {
    console.error("Error during screenshot capture:", error);
  } finally {
    await browser.close();
  }
}

run();
