// chall.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <openssl/sha.h>

#define RV_CODE_SIZE 64     // Max size for our RISC-V machine code
#define ASSEMBLY_BUF_SIZE 1024 // Max size for assembly text input
#define CHAIN_MAX_LEN 10

// --- RISC-V Mini-Emulator ---
typedef struct {
    uint32_t regs[32];
    uint32_t pc;
    uint8_t memory[RV_CODE_SIZE];
} RV32State;

void ecall_handler(RV32State *state) {
    if (state->regs[10] == 1337) {
        printf("ECALL 1337: Nice! Here's your flag!\n");
        FILE *f = fopen("flag.txt", "r");
        if (f) {
            char flag_buf[128];
            fgets(flag_buf, sizeof(flag_buf), f);
            printf("%s\n", flag_buf);
            fclose(f);
        } else {
            printf("infobahn{fakeflag_for_testing}\n");
        }
    } else {
        printf("ECALL %d: Unknown syscall.\n", state->regs[10]);
    }
}

void execute_rv_code(const uint8_t* code) {
    RV32State state = {0};
    memcpy(state.memory, code, RV_CODE_SIZE);
    printf("[*] Starting RISC-V execution...\n");
    while (state.pc < RV_CODE_SIZE) {
        uint32_t instr = *(uint32_t*)&state.memory[state.pc];
        uint32_t opcode = instr & 0x7F;
        if (instr == 0) { break; }
        switch(opcode) {
            case 0x13: { // ADDI
                uint32_t rd = (instr >> 7) & 0x1F;
                uint32_t rs1 = (instr >> 15) & 0x1F;
                int32_t imm = ((int32_t)instr) >> 20;
                if (rd != 0) { state.regs[rd] = state.regs[rs1] + imm; }
                break;
            }
            case 0x73: { // ECALL
                if ((instr >> 20) == 0) {
                    ecall_handler(&state);
                    printf("[*] Execution finished.\n");
                    return;
                }
                break;
            }
            default:
                printf("[!] Unknown opcode: 0x%x\n", opcode);
                return;
        }
        state.pc += 4;
    }
    printf("[*] Execution finished.\n");
}



// Helper to convert register names (e.g., "a0", "x10", "zero") to numbers
int get_reg_num(char *reg_name) {
    // Remove trailing comma if present
    char* comma = strchr(reg_name, ',');
    if (comma) *comma = '\0';

    if (strcmp(reg_name, "zero") == 0 || strcmp(reg_name, "x0") == 0) return 0;
    if (strcmp(reg_name, "ra") == 0 || strcmp(reg_name, "x1") == 0) return 1;
    if (strcmp(reg_name, "sp") == 0 || strcmp(reg_name, "x2") == 0) return 2;
    // ... add more as needed for a harder challenge
    if (strcmp(reg_name, "a0") == 0 || strcmp(reg_name, "x10") == 0) return 10;
    if (strcmp(reg_name, "a1") == 0 || strcmp(reg_name, "x11") == 0) return 11;
    return -1; // Invalid register
}

// Assembles a string of assembly into machine code bytes
int assemble_rv_code(const char *assembly_text, uint8_t *out_buffer) {
    char *text_copy = strdup(assembly_text);
    char *line = strtok(text_copy, "\n");
    int bytes_written = 0;

    while(line != NULL) {
        if (bytes_written >= RV_CODE_SIZE) {
            printf("[!] Assembly code is too large!\n");
            free(text_copy);
            return -1;
        }

        char instr_name[10] = {0};
        sscanf(line, "%9s", instr_name);

        uint32_t machine_code = 0;

        if (strcmp(instr_name, "addi") == 0) {
            char rd_str[10], rs1_str[10];
            int imm;
            if (sscanf(line, "%*s %9s %9s %d", rd_str, rs1_str, &imm) != 3) {
                printf("[!] Invalid ADDI format.\n");
                free(text_copy);
                return -1;
            }
            int rd = get_reg_num(rd_str);
            int rs1 = get_reg_num(rs1_str);

            if (rd == -1 || rs1 == -1) {
                printf("[!] Invalid register name in ADDI.\n");
                free(text_copy);
                return -1;
            }

            machine_code = (imm << 20) | (rs1 << 15) | (0b000 << 12) | (rd << 7) | 0x13;
        } else if (strcmp(instr_name, "ecall") == 0) {
            machine_code = 0x00000073;
        } else if (strlen(instr_name) > 0) {
            printf("[!] Unknown instruction: %s\n", instr_name);
            free(text_copy);
            return -1;
        }

        if (machine_code != 0) {
            memcpy(out_buffer + bytes_written, &machine_code, 4);
            bytes_written += 4;
        }

        line = strtok(NULL, "\n");
    }

    free(text_copy);
    return bytes_written;
}


// --- Blockchain Logic ---
typedef struct {
    int index;
    long timestamp;
    uint8_t data[RV_CODE_SIZE];
    char prev_hash[65];
    char hash[65];
    uint32_t nonce;
} Block;
Block blockchain[CHAIN_MAX_LEN];
int chain_len = 0;
void calculate_hash(Block *b) {
    char input[512];
    unsigned char hash_out[SHA256_DIGEST_LENGTH];
    int len = sprintf(input, "%d%ld%s%u", b->index, b->timestamp, b->prev_hash, b->nonce);
    memcpy(input + len, b->data, RV_CODE_SIZE);
    SHA256((unsigned char*)input, len + RV_CODE_SIZE, hash_out);
    for (int i=0; i < SHA256_DIGEST_LENGTH; i++) { sprintf(b->hash + (i*2), "%02x", hash_out[i]); }
    b->hash[64] = 0;
}
int is_pow_valid(const char* hash) { return strncmp(hash, "000", 3) == 0; }
int is_block_valid(Block *new_block, Block *prev_block) {
    if (new_block->nonce == 0xDEADBEEF) {
        return 1;
    }
    if (new_block->index != prev_block->index + 1) return 0;
    if (strcmp(new_block->prev_hash, prev_block->hash) != 0) return 0;
    char temp_hash[65];
    strcpy(temp_hash, new_block->hash);
    calculate_hash(new_block);
    if (strcmp(new_block->hash, temp_hash) != 0) return 0;
    if (!is_pow_valid(new_block->hash)) return 0;
    return 1;
}
void add_block(Block *b) { if (chain_len < CHAIN_MAX_LEN) { blockchain[chain_len++] = *b; } }
void print_block(Block *b) { printf("\n--- Block %d ---\nTimestamp:  %ld\nPrev Hash:  %s\nNonce:      0x%x\nHash:       %s\nRISC-V Data (%ld bytes)\n------------------\n", b->index, b->timestamp, b->prev_hash, b->nonce, b->hash, sizeof(b->data)); }



int main() {
    setvbuf(stdout, NULL, _IONBF, 0);

    // Create Genesis Block
    Block genesis = {0};
    genesis.index = 0;
    genesis.timestamp = time(NULL);
    strcpy(genesis.prev_hash, "0");
    genesis.nonce = 12345;
    memset(genesis.data, 0, RV_CODE_SIZE);
    calculate_hash(&genesis);
    add_block(&genesis);
    
    printf("A new block has been mined! If its valid, its RISC-V contract will be executed.\n");
    print_block(&genesis);

    // --- UPDATED: Accept a new block from the player ---
    Block new_block = {0};
    new_block.index = blockchain[chain_len - 1].index + 1;
    new_block.timestamp = time(NULL);
    strcpy(new_block.prev_hash, blockchain[chain_len - 1].hash);

    printf("Submit your new block's data.\n");
    printf("Nonce (as hex): ");
    scanf("%x", &new_block.nonce);
    getchar(); // consume newline
    
    printf("Enter your RISC-V assembly contract (end with a blank line):\n");
    char assembly_input[ASSEMBLY_BUF_SIZE] = {0};
    char line_buf[256];
    while(fgets(line_buf, sizeof(line_buf), stdin)) {
        if (strcmp(line_buf, "\n") == 0) {
            break;
        }
        strncat(assembly_input, line_buf, sizeof(assembly_input) - strlen(assembly_input) - 1);
    }
    
    // Assemble the contract into machine code
    int code_size = assemble_rv_code(assembly_input, new_block.data);
    if (code_size < 0) {
        printf("[-] Assembly failed. Rejecting block.\n");
        return 1;
    }
    printf("[+] Assembled %d bytes of machine code.\n", code_size);

    calculate_hash(&new_block);
    
    if (is_block_valid(&new_block, &blockchain[chain_len - 1])) {
        printf("[+] Block is valid! Adding to chain.\n");
        add_block(&new_block);
        print_block(&new_block);
        execute_rv_code(new_block.data);
    } else {
        printf("[-] Block is invalid. Rejected.\n");
    }

    return 0;
}
