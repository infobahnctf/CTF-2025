# XML translator

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [bawolff](https://blog.bawolff.net)                                                         |
| **Category** | web                                                                                         |
| **Solves**   | 2                                                                                           |
| **Files**    | [chall.zip](./chall.zip)                                                                    |

Note: The admin bot lives in the xml-translator-bot directory.

## Hints

### Hint 1

Header injection is not the intended solution.

# Solution

See [solve.py](./solve.py).

PHP's expat compatibility layer had a bug when handling attributes in the xml default handler callback.
It would fail to encode double quote characters. This could mangle the document in a way to
add a namespace declaration and script tag.

e.g.

```
<foo><fo e="&quot;&gt;&lt;/fo&gt;&lt;script xmlns='http://www.w3.org/1999/xhtml'&gt;alert(1)&lt;/script&gt;&lt;fo y=&quot;"/></foo>
```

PHP has since [fixed the issue](https://github.com/php/php-src/issues/20439).
