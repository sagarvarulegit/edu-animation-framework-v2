import puppeteer from 'puppeteer-core';

const assetId = process.argv[2] || 'electric-motor';

async function run() {
  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/google-chrome',
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

  page.on('response', res => {
    if (res.url().includes('.glb') || res.url().includes('asset')) {
      console.log('[RESPONSE]', res.status(), res.url());
    }
  });

  console.log(`Navigating to http://localhost:5173/?asset=${assetId} ...`);
  await page.goto(`http://localhost:5173/?asset=${assetId}`, { waitUntil: 'domcontentloaded' });
  
  await new Promise((r) => setTimeout(r, 5000));

  await page.screenshot({ path: `/tmp/net_${assetId}.png` });
  console.log(`Saved /tmp/net_${assetId}.png`);
  await browser.close();
}

run().catch(e => {
  console.error(e);
  process.exit(1);
});
