import puppeteer from 'puppeteer-core';

const models = [
  'battery',
  'resistor',
  'flower-anatomy',
  'water-electrolysis-apparatus',
  'convex-lens',
  'solenoid',
  'human-respiratory-system',
  'diamond-lattice',
  'optical-bench',
  'human-excretory-system',
  'stoma',
  'nephron',
  'bar-magnet',
  'voltmeter',
  'ammeter',
  'bulb',
  'switch',
  'rheostat',
  'galvanometer'
];

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

  for (const id of models) {
    const url = `http://localhost:5173/?asset=${id}`;
    console.log(`Loading ${id} ...`);
    await page.goto(url, { waitUntil: 'domcontentloaded' });
    try {
      await page.waitForFunction(() => window.__STUDIO_READY__ === true, { timeout: 20000 });
      await new Promise((r) => setTimeout(r, 800));
    } catch (e) {
      console.warn(`Timeout waiting for ${id}, capturing anyway...`);
    }
    const out = `/tmp/review_${id}.png`;
    await page.screenshot({ path: out });
    console.log(`Saved ${out}`);
  }

  await browser.close();
  console.log('Batch capture complete!');
}

run().catch(e => {
  console.error(e);
  process.exit(1);
});
