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
<title>Resume submission</title>
</head>
<body>
<h1>Apply</h1>
<p>
Looking for a job? Submit your resume and we'll be sure to take a look
</p>
<form action="/report" method="post">
<label for="resume">Resume UUID: </label><input name="resume" id="resume">
<br>
<input type="submit" value="Send to admin">
</form>
</body>
</html>
`);

} );
app.post("/report", async (req, res) => {
  if ( req.body.resume === undefined ) {
    return res.sendStatus(400).send( 'Missing resume uuid' );
  }
  const url = APP_URL + '/resumes/' + encodeURI( req.body.resume )

    res.status(200).send("Unfortunately we have a lot of candidates to chose from, so you didn't even make it to the recruiter phone screen. Better luck next time.");
  try {
    await visit(url);
    //return res.status(200).send("Unfortunately we have a lot of candidates to chose from, so you didn't even make it to the recruiter phone screen. Better luck next time.");
  } catch (e) {
    console.error(e);
    //return res.status(500).send("Something wrong");
  }
});

console.log( "Listening on port " + PORT );
app.listen(PORT);
