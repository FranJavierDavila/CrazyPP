// Imprime la guía HTML (720×1020, @page CSS) a PDF con Playwright.
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file:///home/z/my-project/public/descargas/guia-campeonatos-crazy-pingpong.html', { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({
    path: '/home/z/my-project/public/descargas/guia-campeonatos-crazy-pingpong.pdf',
    printBackground: true,
    preferCSSPageSize: true,
  });
  const paginas = await page.evaluate(() => document.querySelectorAll('.chapter-header').length);
  await browser.close();
  console.log('PDF regenerado; chapter-headers en el documento:', paginas);
})().catch(e => { console.error(e); process.exit(1); });
