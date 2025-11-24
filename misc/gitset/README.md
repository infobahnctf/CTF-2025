# gitset

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [rewhile](https://github.com/rewhile)                                                       |
| **Category** | misc                                                                                        |
| **Solves**   | 2                                                                                           |
| **Files**    | [gitset.zip](./gitset.zip)                                                                  |

# Solution

Use `git-init /tmp/...` to initialize a git repo

You can create `pre-receive` hooks using `git-apply --unsafe-paths` since it will allows writing files inside `.git`

Finally trigger rce using a valid `git-receive-pack` payload

Refer to [solve.py](./solve.py) for the implementation.
