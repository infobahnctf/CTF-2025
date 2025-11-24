import puppeteer from "puppeteer";

const sleep = async (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const ext = "/app/extension/";
const FLAG = process.env.FLAG ?? "infobahn{fake_flag}";
const APP_URL = process.env.APP_URL ?? "http://localhost:1337/";

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
      `--disable-extensions-except=${ext}`,
      `--load-extension=${ext}`,
    ],
    dumpio: true,
  });

  try {
    const page1 = await browser.newPage();
    await page1.goto(`${APP_URL}`, { timeout: 3000 });
    await page1.waitForSelector("input[name=username]", { timeout: 3000 });
    await page1.type("input[name=username]", "admin");
    await page1.type("input[name=password]", FLAG);
    await page1.waitForSelector("#infopass-save", { timeout: 3000 });
    await page1.click("#infopass-save");

    await page1.close();

    const page2 = await browser.newPage();
    await page2.goto(url, { timeout: 5000 });
    await sleep(5000);
    await page2.close();
  } catch (e) {
    console.error(e);
  }

  await browser.close();

  console.log(`End visiting: ${url}`);
};
