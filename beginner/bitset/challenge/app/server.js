import puppeteer from "puppeteer";

const php = Bun.spawn(["php", "-S", "127.0.0.1:6969", "-t", "/app"], { stdout: "inherit", stderr: "inherit" });
process.on("exit", () => php.kill());

Bun.serve({
  port: 1337,
  async fetch(req) {
    const u = new URL(req.url);
    if (u.pathname === "/bot") {
      const q = u.searchParams.get("url") || "";
      if (!q) return new Response("url required >:(", { status: 400 });
      if (!/^https?:\/\/.+/i.test(q)) return new Response("url must start with http(s)://", { status: 400 });
      const bot = `http://127.0.0.1:6969/?url=${encodeURIComponent(q)}`;
      const b = await puppeteer.launch({
        executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || "/usr/bin/chromium",
        args: ["--no-sandbox", "--js-flags=--noexpose_wasm,--jitless"],
      });
      try {
        const p = await b.newPage();
        p.setDefaultTimeout(10000);
        await b.setCookie({
          name: "flag",
          value: process.env.FLAG1 || "infobahn{fake_flag1}",
          domain: "127.0.0.1",
          path: "/",
        });
        let flag23;
        if (q.length <= 55) {
          flag23 = process.env.FLAG3 || "infobahn{fake_flag3}";
        } else if (q.length <= 111) {
          flag23 = process.env.FLAG2 || "infobahn{fake_flag2}";
        }
        if (flag23) {
          await p.evaluateOnNewDocument(flag => {
            if (location.hostname == "127.0.0.1") {
              document["flag" + Math.random().toString(36).slice(2)] = flag;
            }
          }, flag23);
        }
        await p.goto(bot, { waitUntil: "domcontentloaded", timeout: 8000 });
        await new Promise(r => setTimeout(r, 3000));
        await b.close();
        return new Response("Cool image (●'◡'●)");
      } finally {
        await b.close();
      }
    }
    u.protocol = "http:";
    u.host = "127.0.0.1:6969";
    const r = await fetch(u, { method: req.method, headers: req.headers, body: req.body, redirect: "manual" });
    return new Response(r.body, { status: r.status, headers: r.headers });
  },
});
