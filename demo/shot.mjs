import puppeteer from 'puppeteer-core';

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const URL = 'http://localhost:5190/';

const browser = await puppeteer.launch({
  executablePath: CHROME,
  headless: 'new',
  args: ['--no-sandbox', '--force-color-profile=srgb'],
});

const page = await browser.newPage();
await page.setViewport({ width: 1440, height: 1000, deviceScaleFactor: 2 });
await page.goto(URL, { waitUntil: 'networkidle0', timeout: 60000 });
await new Promise((r) => setTimeout(r, 1200));

// Full page
await page.screenshot({ path: 'shots/full.png', fullPage: true });

// Per-section shots by anchor id
const sections = ['overview', 'scln', 'demo', 'cases', 'results'];
for (const id of sections) {
  const el = await page.$(`#${id}`);
  if (el) {
    await el.scrollIntoView();
    await new Promise((r) => setTimeout(r, 400));
    await el.screenshot({ path: `shots/${id}.png` });
  }
}

// Hero (top of page)
await page.evaluate(() => window.scrollTo(0, 0));
await new Promise((r) => setTimeout(r, 400));
await page.screenshot({ path: 'shots/hero.png' });

await browser.close();
console.log('done');
