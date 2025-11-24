# unary

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [22sh](https://x.com/0x22sh)                                                                |
| **Category** | beginner                                                                                    |
| **Solves**   | 87                                                                                          |
| **Files**    | [unary.zip](./unary.zip)                                                                    |

# Solution

You can use any unary operators (delete, typeof, void, throw) that require an expression operand. When the parser sees unary/ it treats the / as the start of a regex literal (since division would be invalid there without an expression). It then slurps until the next / to close the regex andd leaving any trailing / as a division operator
and that division "divides" by the RHS, which gets parsed as executable code and so //alert(1) becomes alert(1) because the first / is division, and // starts a comment.

It work also with:

- !/!
- 1/1
- !/1

Intended sol would be to smuggle js in comments

Payload: `!/!;//console.log(process.env.flag)`
