import puppeteer from 'puppeteer-core';

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

  page.on('console', msg => console.log('[LOG]', msg.text()));

  await page.goto('http://localhost:5173/?asset=electric-motor', { waitUntil: 'domcontentloaded' });
  await new Promise(r => setTimeout(r, 4000));

  const info = await page.evaluate(() => {
    const canvas = document.querySelector('canvas');
    if (!canvas) return 'NO CANVAS';
    const ctx = canvas.getContext('webgl2') || canvas.getContext('webgl');
    if (!ctx) return 'NO WEBGL CTX';
    const pixels = new Uint8Array(4);
    ctx.readPixels(canvas.width / 2, canvas.height / 2, 1, 1, ctx.RGBA, ctx.UNSIGNED_BYTE, pixels);
    return {
      width: canvas.width,
      height: canvas.height,
      centerPixel: Array.from(pixels),
      error: ctx.getError(),
    };
  });

  console.log('CANVAS INFO:', info);
  await browser.close();
}

run().catch(console.error);
