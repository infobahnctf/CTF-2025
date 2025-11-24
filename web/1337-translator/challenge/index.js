import express from "express";

import { visit, APP_URL } from "./bot.js";

import { JSDOM } from 'jsdom';
import DOMPurify from 'dompurify';

const PORT = "1337";

const app = express();
app.use(express.urlencoded({ extended: false }));

app.use(express.static("public"));

app.get( "/translate", async (req, res ) => {
  let text = req.query.txt ?? 'Say something!';

  const window = new JSDOM('').window;
  const dp = DOMPurify(window);
  // Don't be naughty
  text = dp.sanitize(text);

  text = text.toUpperCase();
  text = text.replace( /\BA/g, '4' );
  text = text.replace( /\BB/g, 'I3' );
  text = text.replace( /\BE/g, '3' );
  text = text.replace( /\BH/g, '\\-\\' );
  text = text.replace( /\BL/g, '7' );
  text = text.replace( /\BO/g, '0' );
  text = text.replace( /\BS/g, '5' );
  text = text.replace( /\BU/g, 'v' );
  text = text.replace( /\BW/g, 'vv' );

  res.status(200).send( `
<!doctype html><html><head>
<meta charset="UTF-8">
<title>Your message</title>
<style> html { background: black; color: #0b0; color-scheme: dark } </style>
<body>
<h1>MSG</h1>
<div style="padding:1em; margin:1em; border: thin dashed blue; font-family: monospace">
${text}
</div>
</body>
</html>
`); 
} );

app.post("/report", async (req, res) => {
  if ( req.body.txt === undefined ) {
    return res.sendStatus(400).send( 'Missing message' );
  }
  const url = APP_URL + '/translate?txt=' + encodeURIComponent( req.body.txt )

  res.status(200).send( "Checking your message" );
  try {
    await visit(url);
  //  return res.status(200).send("Dope Message");
  } catch (e) {
    console.error(e);
//    return res.status(500).send("Something wrong");
  }
});

console.log( "Listening on port " + PORT );
app.listen(PORT);
