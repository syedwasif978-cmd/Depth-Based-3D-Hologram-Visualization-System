/*
 * UI Smoke Test: serve static frontend and verify dashboard & login elements using Puppeteer
 * Runs a minimal HTTP static server and launches Puppeteer to check key text/content.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

const ROOT = path.resolve(__dirname, '..');
const PORT = process.env.PORT ? Number(process.env.PORT) : 5000;

function contentType(file) {
  const ext = path.extname(file).toLowerCase();
  switch (ext) {
    case '.html': return 'text/html; charset=utf-8';
    case '.js': return 'application/javascript';
    case '.css': return 'text/css';
    case '.svg': return 'image/svg+xml';
    case '.png': return 'image/png';
    case '.jpg': case '.jpeg': return 'image/jpeg';
    default: return 'application/octet-stream';
  }
}

function serveOnce(req, res) {
  let urlPath = decodeURI(req.url.split('?')[0]);
  if (urlPath === '/') urlPath = '/index.html';
  const filePath = path.join(ROOT, urlPath);
  if (!filePath.startsWith(ROOT)) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end('Not found');
      return;
    }
    res.writeHead(200, { 'Content-Type': contentType(filePath) });
    res.end(data);
  });
}

async function runTest() {
  const server = http.createServer(serveOnce).listen(PORT);
  console.log(`Static server started at http://localhost:${PORT}`);

  let browser;
  try {
    browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });
    const page = await browser.newPage();
    page.setDefaultNavigationTimeout(15000);
    await page.goto(`http://localhost:${PORT}/`, { waitUntil: 'domcontentloaded' });
    console.log('Page loaded');

    // Checks
    const checks = await page.evaluate(() => {
      const results = {};
      results.title = document.title || '';
      const logo = document.querySelector('.logo');
      results.logo = logo ? logo.textContent.trim() : null;
      const h1 = document.querySelector('.hero h1');
      results.h1 = h1 ? h1.textContent.trim().replace(/\s+/g, ' ') : null;
      const signupBtn = document.querySelector('.login-box .btn');
      results.signup = signupBtn ? signupBtn.textContent.trim() : null;
      const h2 = document.querySelector('.login-box h2');
      results.h2 = h2 ? h2.textContent.trim() : null;
      return results;
    });

    console.log('Checks:', checks);

    // Simple assertions
    if (!checks.logo || !/Graphite/i.test(checks.logo)) throw new Error('Logo text missing or incorrect');
    if (!checks.h1 || !/next generation/i.test(checks.h1.toLowerCase())) throw new Error('Hero H1 missing or incorrect');
    if (!checks.h2 || !/create your graphite account/i.test(checks.h2.toLowerCase())) throw new Error('Login H2 missing or incorrect');
    if (!checks.signup || !/sign up with github/i.test(checks.signup.toLowerCase())) throw new Error('Signup button missing or incorrect');

    console.log('UI smoke test passed ✅');
    await browser.close();
    server.close();
    process.exit(0);
  } catch (err) {
    console.error('UI smoke test failed ❌', err);
    if (browser) await browser.close().catch(()=>{});
    server.close();
    process.exit(1);
  }
}

runTest();
