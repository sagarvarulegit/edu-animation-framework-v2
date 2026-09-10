import puppeteer from 'puppeteer-core';

const assetId = process.argv[2] || 'beaker';
const outPath = `/tmp/single_${assetId}.png`;

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

  page.on('console', (msg) => console.log(`[BROWSER ${msg.type().toUpperCase()}]`, msg.text()));
  page.on('pageerror', (err) => console.error('[PAGE ERROR]', err));
  page.on('requestfailed', (req) => console.error('[REQUEST FAILED]', req.url(), req.failure()?.errorText));

  console.log(`Navigating to http://localhost:5173/?asset=${assetId} ...`);
  await page.goto(`http://localhost:5173/?asset=${assetId}`, { waitUntil: 'domcontentloaded' });
  
  console.log(`Waiting for window.__STUDIO_READY__ ...`);
  await page.waitForFunction(() => window.__STUDIO_READY__ === true, { timeout: 30000 });
  // Extra second to ensure frame render is fully flushed
  await new Promise((r) => setTimeout(r, 1000));

  const canvasInfo = await page.evaluate(() => {
    const canvas = document.querySelector('canvas');
    if (!canvas) return { error: 'No canvas element found' };
    const rect = canvas.getBoundingClientRect();
    const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
    let pixelSample = null;
    if (gl) {
      const pixels = new Uint8Array(4);
      gl.readPixels(canvas.width / 2, canvas.height / 2, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
      pixelSample = Array.from(pixels);
    }
    return {
      width: canvas.width,
      height: canvas.height,
      rect: { width: rect.width, height: rect.height, top: rect.top, left: rect.left },
      hasGL: !!gl,
      pixelSample,
    };
  });
  console.log('[CANVAS INFO]', JSON.stringify(canvasInfo));

  await page.screenshot({ path: outPath });
  console.log(`Saved ${outPath}`);
  await browser.close();
}

run().catch(e => {
  console.error(e);
  process.exit(1);
});
