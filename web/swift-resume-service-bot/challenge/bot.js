import puppeteer from "puppeteer";

const FLAG = process.env.FLAG ?? "infobhan{fake_flag}";

export const APP_URL = process.env.APP_URL ?? "http://web:80";

const sleep = async (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export const visit = async (url) => {
  console.log(`start: ${url}`);

  if ( (new URL(APP_URL).origin !== new URL(url).origin ) ) {
    console.log( "URL not allowed" )
    return;
  }
  const browser = await puppeteer.launch({
    headless: true,
    executablePath: "/usr/bin/chromium",
    args: [
      "--no-sandbox",
      "--disable-dev-shm-usage",
      "--disable-gpu",
      '--js-flags="--noexpose_wasm"',
    ],
  });

  const context = await browser.createBrowserContext();

  let domain = new URL( APP_URL ).hostname
  context.setCookie( { "domain": domain, "name": "flag", "value": FLAG } );
  try {
    const page1 = await context.newPage();
    await page1.goto(url, { timeout: 5_000, waitUntil: 'networkidle0' });
    await sleep(7_000);
    await page1.close();
  } catch (e) {
    console.error(e);
  }

  await context.close();
  await browser.close();

  console.log(`end: ${url}`);
};
