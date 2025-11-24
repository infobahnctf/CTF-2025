import express from "express";
import rateLimit from "express-rate-limit";
import { visit } from "./bot.js";

const PORT = 1337;
const APP_URL = process.env.APP_URL ?? "http://0.0.0.0:8080/";

const app = express();
app.set("view engine", "ejs");

app.use(express.json());

app.get("/", async (_req, res) => {
  return res.render("./index.ejs");
});

app.use(
  "/",
  rateLimit({
    windowMs: 60 * 1000,
    max: 4,
  })
);

app.post("/", async (req, res) => {
  try {
    await visit(APP_URL);
    return res.send("OK");
  } catch (e) {
    console.error(e);
    return res.status(500).send("Something wrong");
  }
});

app.listen(PORT, () => {
  console.log(`Listening on http://localhost:${PORT}`);
});
