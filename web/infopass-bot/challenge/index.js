import express from "express";
import { visit } from "./bot.js";

const PORT = process.env.PORT ?? "1337";
const APP_URL = process.env.APP_URL ?? "http://localhost:1337/";

const app = express();
app.set("view engine", "ejs");

app.use(express.json());

app.get("/", async (_req, res) => {
  return res.render("./index.ejs", { APP_URL });
});

app.post("/api/report", async (req, res) => {
  const { url } = req.body;
  if (typeof url !== "string" || !/^https?:\/\/.+$/.test(url)) {
    return res.status(400).send("Invalid url");
  }

  try {
    await visit(url);
    return res.send("OK");
  } catch (e) {
    console.error(e);
    return res.status(500).send("Something wrong");
  }
});

app.listen(PORT, () => {
  console.log(`Listening on http://localhost:${PORT}`);
});
