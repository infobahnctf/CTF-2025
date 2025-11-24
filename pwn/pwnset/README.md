# pwnset

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [rewhile](https://github.com/rewhile)                                                       |
| **Category** | pwn                                                                                         |
| **Solves**   | 25                                                                                          |
| **Files**    | [pwnset.zip](./pwnset.zip)                                                                  |

# Solution

Format string bug in `syslog` function, log binary has no PIE no RELRO so we could overwrite GOT

The plan is to overwrite `strtoull@got` with `system`. We can use a partial write with a `1/16` chance because their address are close on libc

`free@got` can also be overwritten to `convert` function

```cpp
snprintf(log, 0x406u, "{'username':'%s','age':%lld}", dest, v7);
syslog(5, log); // Format string
free(log); // free(log) -> convert(log) -> strtoull(log) -> system(log)
```

**Things that didn't happen:**

- Remove waitpid and detach `./log`: Since there's no curl no wget on the server, you will have to figure out a payload to get the flag without using spaces (Since we used scanf for username)

- Sleep inside main so that it matches my work's target (`1/4096` took 3 days to run due to poor hardware)

Refer to [solve.py](./solve.py) for the full exploit.