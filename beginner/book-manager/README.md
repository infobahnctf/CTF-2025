# Book Manager

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [0xM4hm0ud](https://0xm4hm0ud.me/)                                                          |
| **Category** | Beginner                                                                                    |
| **Solves**   | 29                                                                                          |
| **Files**    | [handout.zip](./handout.zip)                                                                  |

# Solution

There are no bound checks when editing a book. You can use negative or positive indexes. There is a callback pointer saved somewhere in the binary. You can edit it and change it to `GetFlag`. After overwriting, you can get the flag with option 5.

See [solve.py](solve.py).
