# blinkenlights

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | programmer_user                                                                             |
| **Category** | Beginner                                                                                    |
| **Solves**   | 63                                                                                          |
| **Files**    | [blinkenlights](blinkenlights)                                                              |

# Solve

The challenge provide us a linux binary:

```sh
❯ file blinkenlights
blinkenlights: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=e6331aad07acb2f9b04bb74400602821d82838db, for GNU/Linux 3.2.0, stripped
```

Looking at the binary on IDA we can see that it fork himself and it's child will open a socket on port 5173. Then it will display ASCII star wars if we connect to it. The parent will connect to the socket and read the first 260 bytes and XOR them to generate an x86 shellcode it will then execute.

```c
__int64 __fastcall main(int a1, char **a2, char **a3)
{
  void *dest; // [rsp+10h] [rbp-20h]
  _BYTE buf[5]; // [rsp+23h] [rbp-Dh] BYREF
  unsigned __int64 v6; // [rsp+28h] [rbp-8h]

  v6 = __readfsqword(0x28u);
  pipe(pipedes);
  pipe(dword_1EC268);
  if ( !fork() )
    sub_1469(dword_1EC268, a2); // Child Function
  close(fd);
  close(dword_1EC268[0]);
  read(pipedes[0], buf, 1uLL);
  sub_1867();   // Parent Function
  dest = mmap(0LL, (unsigned int)n, 7, 34, -1, 0LL);
  memcpy(dest, &unk_1EC120, (unsigned int)n);
  ((void (__fastcall *)(void *, void *))dest)(dest, &unk_1EC280);
  return 0LL;
}
```

```c
void __noreturn sub_1469()  // Child Function
{
  char **v0; // rbx
  size_t v1; // rax
  int v2; // eax
  int optval; // [rsp+0h] [rbp-A0h] BYREF
  socklen_t addr_len; // [rsp+4h] [rbp-9Ch] BYREF
  int i; // [rsp+8h] [rbp-98h]
  int j; // [rsp+Ch] [rbp-94h]
  int k; // [rsp+10h] [rbp-90h]
  int m; // [rsp+14h] [rbp-8Ch]
  int n; // [rsp+18h] [rbp-88h]
  int fd; // [rsp+1Ch] [rbp-84h]
  int v11; // [rsp+20h] [rbp-80h]
  int v12; // [rsp+24h] [rbp-7Ch]
  int v13; // [rsp+28h] [rbp-78h]
  int v14; // [rsp+2Ch] [rbp-74h]
  char *stringp; // [rsp+30h] [rbp-70h] BYREF
  void *ptr; // [rsp+38h] [rbp-68h]
  void *buf; // [rsp+40h] [rbp-60h]
  void *v18; // [rsp+48h] [rbp-58h]
  void *v19; // [rsp+50h] [rbp-50h]
  char *s; // [rsp+58h] [rbp-48h]
  sockaddr addr; // [rsp+60h] [rbp-40h] BYREF
  char v22[5]; // [rsp+7Bh] [rbp-25h] BYREF
  char v23[8]; // [rsp+80h] [rbp-20h] BYREF
  unsigned __int64 v24; // [rsp+88h] [rbp-18h]

  v24 = __readfsqword(0x28u);
  fd = socket(2, 1, 0);
  optval = 1;
  setsockopt(fd, 1, 15, &optval, 4u);
  addr.sa_family = 2;
  *(_DWORD *)&addr.sa_data[2] = 0;
  *(_WORD *)addr.sa_data = htons(0x1435u);
  bind(fd, &addr, 0x10u);
  listen(fd, 3);
  close(pipedes[0]);
  close(dword_1EC26C);
  buf = &unk_2004;
  write(::fd, &unk_2004, 8uLL);
  addr_len = 16;
  v11 = accept(fd, &addr, &addr_len);
  v18 = (void *)"\n";
  v19 = "\x1B[14A\x1B[J";
  v12 = 8;
  for ( i = 0; i <= 13; ++i )
    send(v11, v18, 1uLL, 0);
  v13 = 0;
  stringp = strdup(::s);
  ptr = malloc(8uLL);
  *(_QWORD *)ptr = 0LL;
  for ( j = 1; ; *((_QWORD *)ptr + j - 1) = 0LL )
  {
    s = strsep(&stringp, "\n");
    if ( !s )
      break;
    ptr = realloc(ptr, 8LL * (++j + 1));
    v0 = (char **)((char *)ptr + 8 * j - 16);
    *v0 = strdup(s);
  }
  for ( k = 0; k < j - 1; k += 14 )
  {
    send(v11, v19, v12, 0);
    for ( m = k + 1; m <= k + 13; ++m )
    {
      v1 = strlen(*((const char **)ptr + m));
      v14 = send(v11, *((const void **)ptr + m), v1, 0);
      if ( m != k + 13 )
        send(v11, v18, 1uLL, 0);
    }
    v2 = atoi(*((const char **)ptr + k));
    usleep(67000 * v2);
  }
  read(dword_1EC268[0], v22, 1uLL);
  for ( n = 0; *((_QWORD *)ptr + n); ++n )
    free(*((void **)ptr + n));
  free(ptr);
  do
    read(v11, v23, 1uLL);
  while ( v23[0] != 88 );
  exit(0);
}
```

```c
unsigned __int64 sub_1867() // Parent Function
{
  unsigned int i; // [rsp+0h] [rbp-30h]
  signed int j; // [rsp+4h] [rbp-2Ch]
  int fd; // [rsp+8h] [rbp-28h]
  int v4; // [rsp+Ch] [rbp-24h]
  struct sockaddr addr; // [rsp+10h] [rbp-20h] BYREF
  __int64 buf; // [rsp+20h] [rbp-10h] BYREF
  unsigned __int64 v7; // [rsp+28h] [rbp-8h]

  v7 = __readfsqword(0x28u);
  fd = socket(2, 1, 0);
  addr.sa_family = 2;
  *(_WORD *)addr.sa_data = htons(0x1435u);
  inet_pton(2, "127.0.0.1", &addr.sa_data[2]);
  connect(fd, &addr, 0x10u);
  buf = 88LL;
  for ( i = 0; i < (unsigned int)n; i += v4 )
  {
    v4 = read(fd, &byte_1EC280[i], (unsigned int)n - i);
    if ( v4 == -1 )
      exit(0);
  }
  send(fd, &buf, 1uLL, 0);
  for ( j = 0; j < (unsigned int)n; ++j )
    byte_1EC120[j] ^= byte_1EC280[j];
  return v7 - __readfsqword(0x28u);
}
```

To recover the shellode, we can just NOP the call to the `sub_1867` in the main, connect to the child, read the first 260 bytes and xor it back with `byte_1EC120`.

```py
import socket

N = 260

byte_1EC120 = bytes([0x43,0x83,0xFD,0x43,0x83,0xF4,0x62,0x31,0x2B,0x0B,0x0B, 0x8B,0x3E,0x2E,0x1A,0x5A,0x30,0x35,0x09,0xA3,0x0B,0x2B, 0x79,0x79,0x7D,0x65,0x78,0x6E,0x5A,0x60,0x0B,0x55, 0x60,0x03,0x41,0xA4,0xF3,0x7C,0xC8,0xFD,0x31,0x4B, 0x52,0x05,0x0F,0x3B,0xE0,0x11,0xDF,0x4A,0x05,0x7A,0x68, 0xA9,0xC6,0x2F,0x25,0x68,0xE7,0xE1,0x20,0x20,0x20,0x20,0x68, 0xA3,0xD9,0x05,0x5D,0x5B,0x16,0xDD,0x2A,0x4E,0x63,0x47, 0x45,0x01,0xB2,0x80,0xBF,0xA7,0x07,0xC7,0xC8,0x0B,0xF7, 0x2F,0x4F,0x5B,0x0B,0x0B,0x0B,0x21,0x21,0x70,0x68,0x98, 0x19,0x13,0x08,0x4A,0x6D,0x21,0x21,0x21,0x68,0x11,0x24,0x04, 0x68,0x98,0x1C,0x19,0x1F,0x75,0x4B,0x13,0x4E,0x1B,0x70, 0x68,0xC8,0x73,0x21,0x01,0x21,0x06,0x53,0x4A,0x72,0x5A, 0x42,0xB2,0x7B,0x25,0x0E,0x55,0x0D,0x3C,0x5F,0x68,0x1A, 0x42,0xB2,0x69,0x6E,0x66,0x6F,0x62,0x61,0x68,0x6E,0x5A, 0x42,0x92,0xBC,0x79,0xF3,0x80,0x3E,0x5B,0x4A,0x20, 0xD3,0x86,0x55,0x00,0x66,0x96,0x2F,0x2F,0x2F,0x2F,0x2F,0x2F,0x2F,0x21,0x70,0x68, 0x98,0x73,0x48,0x46,0x49,0x55,0x2B,0x21,0x41,0x08,0x71, 0x44,0x64,0x4A,0x21,0x7F,0x4A,0x46,0x1A,0x08,0xC9,0xA6, 0x44,0x2F,0x76,0x21,0x2B,0x1F,0xD1,0x60,0x1C,0x78,0x2F, 0x25,0x68,0x96,0x2F,0x2F,0x2F,0x2F,0x2F,0x2F,0x2F,0x2F,0x70,0x68,0x98,0x76,0x53, 0x4E,0x4F,0x46,0x2B,0x21,0x41,0x68,0x11,0x24,0x04,0x4A, 0x41,0x7F,0x4A,0x46,0x7A,0x68,0xA9,0xC6,0x4A,0x41, 0x76,0x21,0x2B,0x1F,0xD1,0x44,0x12,0x52,0x2F,0x25])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 5173))

payload = b''
while len(payload) < N:
    chunk = s.recv(N - len(payload))
    if not chunk:
        break
    payload += chunk

print(f'received {len(payload)} bytes')
shellcode = bytes(a ^ b for a, b in zip(byte_1EC120, payload))
print(shellcode)
open("shellcode.bin", "wb").write(shellcode)
```

Once we have recovered the shellcode, we can analyze it with this script:

```py
from capstone import *
from capstone.x86 import *

shell = open("shellcode.bin", "rb").read()

md = Cs(CS_ARCH_X86, CS_MODE_64)
md.detail = True

insns = list(md.disasm(shell, 0x0))

def fmt_op(op):
    if op.type == X86_OP_REG:
        return insn.reg_name(op.reg)
    if op.type == X86_OP_IMM:
        return "0x{:x}".format(op.imm)
    if op.type == X86_OP_MEM:
        seg = ""
        base = ""
        idx = ""
        disp = ""
        if op.mem.base != 0:
            base = insn.reg_name(op.mem.base)
        if op.mem.index != 0:
            idx = insn.reg_name(op.mem.index)
        if op.mem.disp != 0:
            disp = "{:#x}".format(op.mem.disp)
        mem = ""
        if base:
            mem += base
        if idx:
            mem += "+" + idx
        if disp:
            mem += "+" + disp
        return "[" + mem + "]"
    return "?"

print(f"Shellcode length: {len(shell)} bytes\n")
for insn in insns:
    print("0x{:<03x}:\t{:<8}\t{}".format(insn.address, insn.mnemonic, insn.op_str))
```

Which gives us this assembly:

```
Shellcode length: 260 bytes

0x000:	mov     	r15, rsi
0x300:	mov     	r14, rdi
0x600:	push    	0x101213b
0xb00:	xor     	dword ptr [rsp], 0x1010101
0x120:	movabs  	rax, 0x64726f7773736150
0x1c0:	push    	rax
0x1d0:	push    	1
0x1f0:	pop     	rdi
0x200:	push    	9
0x220:	pop     	rdx
0x230:	inc     	edx
0x250:	mov     	rsi, rsp
0x280:	push    	1
0x2a0:	pop     	rax
0x2b0:	syscall
0x2d0:	xor     	eax, eax
0x2f0:	xor     	edi, edi
0x310:	push    	0x25
0x330:	pop     	rdx
0x340:	mov     	rsi, rsp
0x370:	syscall
0x390:	mov     	rcx, 0
0x400:	cmp     	rcx, 0x25
0x440:	jge     	0x52
0x460:	mov     	al, byte ptr [r15 + rcx]
0x4a0:	xor     	byte ptr [rsp + rcx], al
0x4d0:	inc     	rcx
0x500:	jmp     	0x40
0x520:	mov     	rsi, rsp
0x550:	movabs  	rax, 0x101010101010101
0x5f0:	push    	rax
0x600:	movabs  	rax, 0x101014d6a283339
0x6a0:	xor     	qword ptr [rsp], rax
0x6e0:	movabs  	rax, 0x3b6e336b553f393c
0x780:	push    	rax
0x790:	movabs  	rax, 0x7839276844724401
0x830:	push    	rax
0x840:	movabs  	rax, 0x33447d3964553e71
0x8e0:	push    	rax
0x8f0:	movabs  	rax, 0x64626b68656c6463
0x990:	push    	rax
0x9a0:	mov     	rdi, rsp
0x9d0:	mov     	rcx, 0x25
0xa40:	repe cmpsb	byte ptr [rsi], byte ptr [rdi]
0xa60:	jne     	0xd6
0xa80:	movabs  	rax, 0x101010101010101
0xb20:	push    	rax
0xb30:	movabs  	rax, 0x1010b7569666853
0xbd0:	xor     	qword ptr [rsp], rax
0xc10:	push    	1
0xc30:	pop     	rdi
0xc40:	push    	6
0xc60:	pop     	rdx
0xc70:	mov     	rsi, rsp
0xca0:	push    	1
0xcc0:	pop     	rax
0xcd0:	syscall
0xcf0:	xor     	edi, edi
0xd10:	push    	0x3c
0xd30:	pop     	rax
0xd40:	syscall
0xd60:	movabs  	rax, 0x101010101010101
0xe00:	push    	rax
0xe10:	movabs  	rax, 0x1010b666f6e7356
0xeb0:	xor     	qword ptr [rsp], rax
0xef0:	push    	1
0xf10:	pop     	rdi
0xf20:	push    	6
0xf40:	pop     	rdx
0xf50:	mov     	rsi, rsp
0xf80:	push    	1
0xfa0:	pop     	rax
0xfb0:	syscall
0xfd0:	xor     	edi, edi
0xff0:	push    	0x3c
0x101:	pop     	rax
0x102:	syscall
```

We can see that the shellcode first prints "Password: ", reads 37 bytes, then XOR the input with the first 37 bytes of the star wars stream of the remote (it is passed via rsi from the parent). It then builds the expected password on the stack and compare if our xored input match.

**solve.py**

```py
expected = bytes.fromhex("63646c65686b6264713e5564397d443301447244682739783c393f556b336e3b383232296b4c")
xor_stream = bytes.fromhex("0a0a0a0a0a0a0a0a0a0a0a0a0a0a1b5b3134411b5b4a0a0a0a0a0a0a0a0a0a0a0a0a1b5b31")

flag = bytes(a ^ b for a, b in zip(expected, xor_stream))
print(flag)
```
