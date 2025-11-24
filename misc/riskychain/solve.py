#!/usr/bin/env python3

from pwn import *
import sys

def solve_challenge(host='localhost', port=1337):
    """Connect to the challenge and submit the exploit."""
    
    context.timeout = 10
    
    io = remote(host, port)
    
    log.info("Receiving genesis block...")
    io.recvuntil(b"Nonce (as hex):")
    
    log.info("Sending magic nonce 0xDEADBEEF...")
    io.sendline(b"DEADBEEF")
    
    io.recvuntil(b"Enter your RISC-V assembly contract")
    
    log.info("Sending RISC-V assembly:")
    io.sendline(b"addi a0, zero, 1337")
    io.sendline(b"ecall")
    io.sendline(b"")  # Empty line to end input
    
    log.info("Receiving response...")
    try:
        response = io.recvall()
        print(response.decode('utf-8', errors='ignore'))
    except Exception as e:
        log.warning(f"Error receiving response: {e}")
    finally:
        io.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        host = sys.argv[1]
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 1337
    else:
        host = 'localhost'
        port = 1337
    
    solve_challenge(host, port)
