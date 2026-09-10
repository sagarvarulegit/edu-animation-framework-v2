import puppeteer from 'puppeteer-core';

async function run() {
  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/google-chrome',
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--enable-unsafe-swiftshader'],
  });

  const page = await browser.newPage();
  await page.goto('http://localhost:5173', { waitUntil: 'domcontentloaded' });
  await new Promise(r => setTimeout(r, 2000));

  const result = await page.evaluate(async () => {
    try {
      const { GLTFLoader } = await import('/node_modules/.vite/deps/three_examples_jsm_loaders_GLTFLoader__js.js?v=20940c88');
      const loader = new GLTFLoader();
      return new Promise((resolve, reject) => {
        loader.load(
          '/assets/electric-motor.glb',
          (gltf) => {
            resolve({
              success: true,
              children: gltf.scene.children.map(c => c.name),
            });
          },
          undefined,
          (err) => {
            resolve({ success: false, error: String(err) });
          }
        );
      });
    } catch (e) {
      return { caught: String(e), stack: e.stack };
    }
  });

  console.log('LOAD RESULT:', result);
  await browser.close();
}

run().catch(console.error);
