from secrets import token_bytes
from functools import reduce
import subprocess
import tempfile
import os

FLAG = b'infobahn{readREADr34dRe4drE4D}'
FLAGS_COUNT = 5

def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

flags = []
for i in range(FLAGS_COUNT - 1):
    flags.append(token_bytes(len(FLAG)))
flags.append(xor(reduce(xor, flags), FLAG))
assert reduce(xor, flags) == FLAG

blacklist = set()
for i, flag in enumerate(flags):
    with tempfile.TemporaryDirectory() as temp_dir:
        flag_path = os.path.join(temp_dir, 'flag.txt')
        with open(flag_path, 'wb') as f:
            f.write(flag)

        os.chmod(temp_dir, 0o755)
        os.chmod(flag_path, 0o644)

        try:
            user_input = bytes.fromhex(input(f"Enter your input as hex ({i+1}/{FLAGS_COUNT}):").strip())
            for byte in user_input:
                if byte in blacklist:
                    print("You already used " + hex(byte))
                    exit()
            blacklist = blacklist.union(set(user_input))

            p = subprocess.run(
                ['sudo', '-u', 'restricted', '/binary'],
                capture_output=True,
                input=user_input,
                timeout=2.0,
                cwd=temp_dir
            )

            print("stdout:", p.stdout)
        except Exception as e:
            print("Error:", e)
            exit()