import express from "express";

import { visit, APP_URL } from "./bot.js";

const PORT = "1337";

const app = express();
app.use(express.urlencoded({ extended: false }));

app.use(express.static("public"));

app.get( "/", async ( req, res ) => {
  return res.send( `
<!doctype html>
<html>
<head>
<title>1337 XML converter repot bot</title>
</head>
<body>
<h1>XML 1337 Report bot</h1>
<p>
Have a file you want to convert. Give it to me and I'll put it into the website for you.
</p>
<label>XML:</label><br>
<form action="/report" method="POST">
<textarea name="xml" id="xml" cols="80" rows="15" placeholder="<&#x3f;xml version=&quot;1.0&quot;&#x3f;>" required>
</textarea>
<br>
<input type="submit" value="Send to admin">
</form>
</body>
</html>
`);

} );
app.post("/report", async (req, res) => {
  if ( req.body.xml === undefined ) {
    return res.sendStatus(400).send( 'Missing xml' );
  }
  const url = APP_URL + '/?xml=' + encodeURIComponent( req.body.xml )

  res.status(200).send( "I'll be sure to look when i have a moment." );
  try {
    await visit(url);
//    return res.status(200).send("Dope file");
  } catch (e) {
    console.error(e);
//    return res.status(500).send("Something wrong");
  }
});

console.log( "Listening on port " + PORT );
app.listen(PORT);
