<?php
$IMG = 'https://i.imgur.com/nh16rl8.png';
$url = $_GET['url'] ?? $IMG;

if ($url !== '' && !preg_match('/^https?:\/\/.+/i', $url)) {
  http_response_code(400);
  header('Content-Type: text/plain; charset=utf-8');
  echo 'url must start with http(s)://';
  exit;
}

function render_img_markdown(string $s): string {
  return preg_replace(
    '/!\[ \]\(([^)\r\n]*)\)/',
    "<img src='$1' loading='lazy'>",
    htmlspecialchars('![ ](' . $s . ')', ENT_HTML5, 'UTF-8')
  );
}
?>
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>bitset's image sharer</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <link rel="stylesheet" href="https://cdn.simplecss.org/simple.min.css">
</head>
<body>
  <h1>bitset's image sharer</h1>

  <form method="get" autocomplete="off" novalidate>
    <label for="url"><strong>Image URL</strong></label>
    <input id="url" name="url" type="url" placeholder="<?= $IMG ?>" required>
    <button type="submit">Preview</button>
  </form>

  <h2>Preview</h2>
  <div><?= render_img_markdown($url) ?></div>

  <p>
    <button type="button" id="share-image">Share image</button>
  </p>
  <script>
    const IMG = <?= json_encode($IMG) ?>;
    document.getElementById('share-image').addEventListener('click', function () {
      const params = new URLSearchParams(location.search);
      const imgUrl = params.get('url') || IMG;
      location.href = '/bot?url=' + encodeURIComponent(imgUrl);
    });
  </script>
</body>
</html>
