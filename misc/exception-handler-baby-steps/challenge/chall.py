#!/usr/local/bin/python3 -u

import os

def run_chal():
    if 0x43 in range(0x21):
        print("GG!", flush=True)
        os.execv("/bin/sh", ["sh"])
    
    1 / 0

exc_table = bytes.fromhex(input("Exception Table > "))
run_chal.__code__ = run_chal.__code__.replace(co_exceptiontable=exc_table)

run_chal()