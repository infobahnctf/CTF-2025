# Swift resume service

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [bawolff](https://blog.bawolff.net)                                                         |
| **Category** | web                                                                                         |
| **Solves**   | 0                                                                                           |
| **Files**    | [chall.zip](./chall.zip)                                                                    |

Note: The admin bot lives in the swift-resume-service-bot directory.

Note: It is normal for this challenge to take a really long time to build.

## Hints

### Hint 1

As far as we know, swift-soup correctly sanitizes the HTML. The intended solution does not involve swift-soup doing something wrong.

### Hint 2

Sometimes library functions can have unintuitive behaviour.

# Solution

See [solve.sh](./solve.sh).

The main idea of this challenge is to exploit the fact that [in swift](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/stringsandcharacters/#Extended-Grapheme-Clusters), a character is considered a unicode
extended grapheme cluster, where the rest of the world works on unicode code points.

An [extended grapheme cluster](http://www.unicode.org/reports/tr29/#Grapheme_Cluster_Boundaries) is what humans would consider a "character". In essence it is a base character
plus any combining characters.

For example an O with an X overtop (oͯ) is 2 unicode characters but 1 extended grapheme cluster.

The Swift `replacingOccurrences` works on these extended grapheme clusters by default.

In the challenge we had code like `text = text.replacingOccurrences( of: "\"", with: "&quot;" )`

This would replace `"` with its entity representation. However if you had something like "́ (A double quote followed by a combining accute accent) it would not replace it since a double quote by itself is a different grapheme cluster than a double quote plus a combining character. HTML of course just sees this as a normal double quote followed by some other random character.

Thus you could bypass the sanitization routine by adding combining characters to html special characters. This could be used to break out of attributes and get XSS.
