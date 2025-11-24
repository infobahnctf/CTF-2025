#!/usr/bin/env python3
import sys
import subprocess
import tempfile

def main():
    try:
        size = int(input("Enter solve script file size: ").strip())
    except ValueError:
        print("Invalid size input.")
        return 1

    if size >= 20000:
        print(f"Error: input size {size} exceeds allowed limit.")
        return 1

    print("Waiting for script content...")
    script = sys.stdin.read(size)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=True) as tmp:
        tmp.write(script)
        tmp.flush()
        print(f"Executing script via d8 (timeout: 15s)...")
        try:
            subprocess.run(["./d8", tmp.name], timeout=15, check=False)
        except subprocess.TimeoutExpired:
            print("Execution timed out after 15 seconds.")

    print("Execution finished.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
