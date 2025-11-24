# SAML

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [bawolff](https://blog.bawolff.net)                                                         |
| **Category** | web                                                                                         |
| **Solves**   | 14                                                                                          |
| **Files**    | [chall.zip](./chall.zip)                                                                    |

Note, the SP part of this challenge lives in saml-sp directory

# Solution

- Click view flag
- Register an account named `ak&:123;`
- Login. Go to flag page, getting error message saying you can't view flag
- Take url that has ?SAMLResponse parameter in it. Take just the value of that parameter
- Run the fixToken.py script with the value of the SAMLResponse url parameter as the first argument
- Take the output of that script, and replace the SAMLResponse url parameter with that value
- You should have the flag

General idea: The js xml-crypto library doesn't handle entity references that don't match `\w` properly. It
thinks that `ak&amp;:123;` will have the same hash as `ak&:123;` no matter what the :123 entity is set to.
Thus we register an account with &:123; in it, then we replace the escaped version of it with the unescaped
version and add a DTD with an internal subset setting the value of &:123; to whatever we want. This allows
us to login as anyone without invalidating the digital signature on the XML document.

The xml-crypto node library ignores DTDs however JSDom supports them (or at least entities. It doesn't seem to properly support attribute normalization), thus there is a parser differential between the two libraries.

The challenge also had an unintended XML signature wrapping vulnerability, where you could put an extra assertion element inside the signature element which would be ignored when checking the signature but still be used for finding the user's name.
