# Sandbox Viewer

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [0xAlessandro](https://0xalessandro.github.io/)                                             |
| **Category** | web                                                                                         |
| **Solves**   | 2                                                                                           |
| **Files**    | [chall.zip](./chall.zip)                                                                    |

# Solution

- dompurify was loaded from cdn, the onerror logic is the branch you want to fall into
- your input is first put into a sandboxed iframe(no js) and then sanitised with dompurify (you cannot escape from the challenge, a meta tag redirect wouldn’t work → dompurify sanitises meta tag and the sandboxed iframe would trhow an error)
- the idea is to pollute the browser disk cache, dompurify is loaded from cloudfare cdn(which use cloudfare waf) → if the waf sees a dangerous referrer header it will return a 403
- since your input is put into the dom before the script load, you can use make an image element with a malicious referrer point to the dompurify cdn url, it will store a 403 response.
- the dompurify script, appended to the dom later, will reuse the image response(403) from disk cache instead of requesting the dompurify url again, making the script fall into the onerror branch

Refer to [solve.py](./solve.py) for the solution
