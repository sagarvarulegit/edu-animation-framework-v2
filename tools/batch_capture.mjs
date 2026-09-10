import puppeteer from 'puppeteer-core';

const modelsToCapture = [
  'bunsen-burner',
  'beaker',
  'human-heart',
  'magnesium-burning-setup',
  'human-eye',
  'electric-motor',
  'battery',
  'resistor',
  'flower-anatomy',
  'water-electrolysis-apparatus',
  'convex-lens',
  'solenoid',
  'human-respiratory-system',
  'diamond-lattice',
  'optical-bench'
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

  for (const id of modelsToCapture) {
    const url = `http://localhost:5173/?asset=${id}`;
    console.log(`Loading ${id} via ${url} ...`);
    await page.goto(url, { waitUntil: 'networkidle0', timeout: 20000 });
    await new Promise((r) => setTimeout(r, 2200));
    const out = `/tmp/review_${id}.png`;
    await page.screenshot({ path: out });
    console.log(`Saved ${out}`);
  }

  await browser.close();
}

run().catch(e => {
  console.error(e);
  process.exit(1);
});
