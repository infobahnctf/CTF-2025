from quart import Quart, Response, request
import html
import base64

app = Quart(__name__)
idx = """
<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Our logo</title>
  <style>
    :root { color-scheme: light dark; }
    body {
      margin: 0; min-height: 100svh; display: grid; place-items: center;
      font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
      background: Canvas; color: CanvasText;
    }
    img { max-width: min(80vw, 320px); height: auto; display: block; }
  </style>
</head>
<body>
  <img src="data:image/png;base64,%s" alt="This is our logo">
</body>
</html>
"""
with open("logo.png", "rb") as f:
    logo = f.read()
    idx = idx % base64.b64encode(logo).decode()


@app.route("/")
async def index():
    return idx