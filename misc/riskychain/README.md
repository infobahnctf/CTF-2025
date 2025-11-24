# Risky Chain

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [vielite](https://github.com/VIELITE)                                                       |
| **Category** | misc                                                                                        |
| **Solves**   | 148                                                                                         |
| **Files**    | [risc-v](./risc-v)                                                                          |

# Solution

You can decompile the binary and see that the emulator supports two instructions:

- **ADDI** (opcode `0x13`): Adds an immediate value to a register
- **ECALL** (opcode `0x73`): System call instruction

```c
void execute_rv_code(const uint8_t* code) {
    RV32State state = {0};
    memcpy(state.memory, code, RV_CODE_SIZE);
    // ...
}
```

In the `ecall_handler` it checks if register `a0` (register 10) equals 1337:

```c
void ecall_handler(RV32State *state) {
    if (state->regs[10] == 1337) {
        printf("ECALL 1337: Nice! Here's your flag!\n");
        FILE *f = fopen("flag.txt", "r");
    }
}
```

And in `is_block_valid`:

```c
int is_block_valid(Block *new_block, Block *prev_block) {
    if (new_block->nonce == 0xDEADBEEF) {
        return 1;  // bypass all
    }
    // ... normal validation checks ...
}
```

So u just craft a riscv assembly like

```asm
addi a0, zero, 1337    ; Set a0 = 0 + 1337 = 1337
ecall                   ; Trigger system call
```

Refer to [solve.py](./solve.py) for the implementation.

```
[*] Opening connection to localhost on port 1337: Done
[*] Reading genesis block...
[*] Sending magic nonce 0xDEADBEEF to bypass PoW...
[*] Sending RISC-V assembly exploit...
[*] Waiting for execution...

[+] Assembled 8 bytes of machine code.
[+] Block is valid! Adding to chain.

--- Block 1 ---
Timestamp:  1762708816
Prev Hash:  d0d1ab69f3429e5c4ff1290d0620e2cfdf20ea2713d0cad438aaddeb4e7e4a5f
Nonce:      0xdeadbeef
Hash:       be866de60c85804870ee7090cd3ff920cd6e55a46da36cc3912a23e7910a8dec
RISC-V Data (64 bytes)
------------------
[*] Starting RISC-V execution...
ECALL 1337: Nice! Here's your flag!
infobahn{...}

[*] Execution finished.
```
