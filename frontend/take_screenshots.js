import puppeteer from 'puppeteer';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const outDir = 'C:\\Users\\sande\\.gemini\\antigravity\\brain\\4b2ff587-ec38-4d03-8fc2-69aa5da29df9';

async function run() {
  console.log("Launching browser...");
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  
  try {
    console.log("Navigating to app...");
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle0' });
    
    // 1. Desktop Empty State
    await page.setViewport({ width: 1280, height: 800 });
    await page.screenshot({ path: path.join(outDir, 'desktop_empty.png'), fullPage: true });
    console.log("Captured desktop_empty.png");

    // 2. Desktop Analyzed State (Negative Sentiment)
    await page.waitForSelector('textarea', { timeout: 10000 });
    await page.type('textarea', 'I felt really overwhelmed at work today and thought I was going to get fired. It was terrible.');
    
    // Click Analyze button
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const analyzeBtn = buttons.find(b => b.textContent.includes('Analyze'));
      if (analyzeBtn) analyzeBtn.click();
    });

    console.log("Waiting for analysis...");
    // Wait for result card to appear
    await page.waitForFunction(() => {
      return document.body.innerText.includes('Analysis Overview');
    }, { timeout: 30000 });
    
    // Wait for animations
    await new Promise(r => setTimeout(r, 2000));
    
    await page.screenshot({ path: path.join(outDir, 'desktop_analyzed.png'), fullPage: true });
    console.log("Captured desktop_analyzed.png");

    // 3. Desktop Analytics Tab
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('.hidden.md\\:flex button'));
      const analyticsBtn = buttons.find(b => b.textContent.includes('Analytics'));
      if (analyticsBtn) analyticsBtn.click();
    });
    
    // wait for charts
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, 'desktop_analytics.png'), fullPage: true });
    console.log("Captured desktop_analytics.png");

    // 4. Mobile Breakpoint Check (Analytics tab)
    console.log("Switching to mobile viewport...");
    await page.setViewport({ width: 375, height: 812, isMobile: true, hasTouch: true });
    await new Promise(r => setTimeout(r, 500));
    // Do NOT use fullPage: true for mobile, so we see the fixed navbar in the viewport
    await page.screenshot({ path: path.join(outDir, 'mobile_analytics.png') });
    console.log("Captured mobile_analytics.png");

    // 5. Mobile Journal Tab
    await page.evaluate(() => {
      // Find mobile bottom nav buttons
      const buttons = Array.from(document.querySelectorAll('.md\\:hidden button'));
      const journalBtn = buttons.find(b => b.textContent.includes('Journal'));
      if (journalBtn) journalBtn.click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, 'mobile_journal.png') });
    console.log("Captured mobile_journal.png");

    // 6. Mobile History Tab
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('.md\\:hidden button'));
      const historyBtn = buttons.find(b => b.textContent.includes('History'));
      if (historyBtn) historyBtn.click();
    });
    await new Promise(r => setTimeout(r, 1000));
    
    // Scroll to bottom to show padding
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await new Promise(r => setTimeout(r, 500));
    
    await page.screenshot({ path: path.join(outDir, 'mobile_history.png') });
    console.log("Captured mobile_history.png");

  } catch (error) {
    console.error("Error during screenshot capture:", error);
  } finally {
    await browser.close();
  }
}

run();
