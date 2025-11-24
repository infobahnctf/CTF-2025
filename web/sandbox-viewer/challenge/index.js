const path = require("path");
const express = require("express");
const puppeteer = require("puppeteer");
const app = express();
//get port from the env
const port = process.env.PORT || 1337;

app.use((req, res, next) => {
    res.setHeader("X-Frame-Options", "SAMEORIGIN");
    res.setHeader("X-Content-Type-Options", "nosniff");
    res.setHeader("Content-Security-Policy", "base-uri 'none'; object-src 'none'");
    next();
});

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function visitUrl(key, timeout = 15000) {
    let browser;
    try {
        console.log('[BOT] Starting browser...');

        browser = await puppeteer.launch({
            args: [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--disable-extensions',
            ],
            headless: true,
            executablePath: "/usr/bin/chromium",
            devtools: false,
            dumpio: false,
        });

        const origin = `http://localhost:${port}`;


        const context = browser.defaultBrowserContext();
        const page = await browser.newPage();


        const client = await page.target().createCDPSession();
        await client.send('Network.clearBrowserCache');
        await client.send('Network.clearBrowserCookies');

        // Capture console messages from the browser
        page.on('console', msg => {
            const type = msg.type();
            const text = msg.text();
            console.log(`[BROWSER ${type.toUpperCase()}] ${text}`);
        });

        // Capture dialog (alert, confirm, prompt)
        page.on('dialog', async dialog => {
            console.log(`[BROWSER DIALOG] ${dialog.type()}: ${dialog.message()}`);
            await dialog.dismiss();
        });

        const url = `${origin}/?key=${encodeURIComponent(key)}`;
        console.log('[BOT] Visiting:', url);
        //set the cookie for localhost
        await context.setCookie({
            name: 'admin',
            value: 'infobahn{D1sk_C4che_t0_th3_r3scue}',
            domain: `localhost`,
            path: '/',
            httpOnly: false,
            sameSite: 'Lax'
        });
        await page.goto(url);

        console.log(`[BOT] Waiting ${timeout}ms before closing...`);
        await sleep(timeout);
        console.log('[BOT] Visit completed successfully');

        console.log('[BOT] Closing browser...');
    } finally {
        try { if (browser) await browser.close(); } catch { }
    }
}
// Serve the challenge page
app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "index.html"));
});

// Report route: call visitUrl and also serve the page
app.get("/report", async (req, res) => {
    const key = req.query.key || "";
    if (!key) {
        return res.status(400).send("Missing key parameter");
    }
    visitUrl(key);

    res.send("OK");
});

app.listen(port, () => {
    console.log("Server is running on port " + port);
});