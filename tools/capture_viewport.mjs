import puppeteer from 'puppeteer-core';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const assetId = process.argv[2] || 'glass-prism-refraction';
const outPath = process.argv[3] || path.join(os.tmpdir(), `capture_${assetId}.png`);

function findChromeExecutable() {
  if (process.env.CHROME_PATH && fs.existsSync(process.env.CHROME_PATH)) {
    return process.env.CHROME_PATH;
  }
  const candidates = [
    // Windows
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    // Linux
    '/usr/bin/google-chrome',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
    // macOS
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ];
  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }
  return '/usr/bin/google-chrome';
}

async function run() {
  const executablePath = findChromeExecutable();
  const browser = await puppeteer.launch({
    executablePath,
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--enable-unsafe-swiftshader',
      '--use-gl=angle',
      '--use-angle=swiftshader',
      '--window-size=1280,800',
    ],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  page.on('console', (msg) => {
    console.log(`[BROWSER ${msg.type().toUpperCase()}]`, msg.text());
  });

  page.on('pageerror', (err) => {
    console.error('[PAGE ERROR]', err);
  });

  page.on('requestfailed', (req) => {
    console.error('[REQUEST FAILED]', req.url(), req.failure()?.errorText);
  });

  console.log(`Navigating to http://localhost:5173 ...`);
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle0', timeout: 20000 });

  // If specific asset requested, click on sidebar item
  if (assetId !== 'glass-prism-refraction') {
    console.log(`Selecting asset: ${assetId}`);
    await page.evaluate((id) => {
      const btns = Array.from(document.querySelectorAll('button'));
      const btn = btns.find((b) => b.textContent?.toLowerCase().includes(id.toLowerCase()));
      if (btn) btn.click();
    }, assetId);
    await new Promise((r) => setTimeout(r, 2000));
  }

  await new Promise((r) => setTimeout(r, 3000));

  await page.screenshot({ path: outPath });
  console.log(`Screenshot saved to ${outPath}`);

  await browser.close();
}

run().catch((e) => {
  console.error(e);
  process.exit(1);
});
