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

  const debugInfo = await page.evaluate(() => {
    const canvas = document.querySelector('canvas');
    if (!canvas) return { error: 'No canvas found' };
    const r3f = canvas.__r3f;
    if (!r3f) return { error: 'No __r3f found on canvas' };
    const state = r3f.root?.store?.getState?.();
    if (!state) return { error: 'No r3f state' };
    const { camera, scene } = state;
    
    const objects = [];
    scene.traverse(obj => {
      objects.push({
        name: obj.name,
        type: obj.type,
        visible: obj.visible,
        pos: [obj.position.x, obj.position.y, obj.position.z],
        scale: [obj.scale.x, obj.scale.y, obj.scale.z]
      });
    });

    return {
      camPos: [camera.position.x, camera.position.y, camera.position.z],
      camNear: camera.near,
      camFar: camera.far,
      camFov: camera.fov,
      objectCount: objects.length,
      objects: objects.slice(0, 30),
    };
  });

  console.log('DEBUG INFO:', JSON.stringify(debugInfo, null, 2));
  await browser.close();
}

run().catch(console.error);
