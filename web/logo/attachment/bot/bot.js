import puppeteer from "puppeteer";

const sleep = async (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const FLAG = process.env.FLAG ?? "infobahn{fake_flag}";
const APP_URL = process.env.APP_URL ?? "http://logo:tmp_pass@localhost:8080/";

export const visit = async (url) => {
  console.log(`Start visiting: ${url}`);

  const browser = await puppeteer.launch({
    headless: "new",
    pipe: true,
    executablePath: "/usr/bin/chromium",
    args: [
      "--no-sandbox",
      "--disable-setuid-sandbox",
      "--disable-dev-shm-usage",
      "--disable-gpu",
      '--js-flags="--noexpose_wasm"',
    ],
    dumpio: true,
  });

  try {

    await browser.setCookie({
      "name": "flag",
      "value": FLAG,
      "domain": new URL(APP_URL).hostname,
      "path": "/",
      "httpOnly": false,
    })

    const page = await browser.newPage();
    await page.goto(url, { timeout: 5000 });
    await sleep(3000);
    await page.close();
  } catch (e) {
    console.error(e);
  }

  await browser.close();

  console.log(`End visiting: ${url}`);
};
