# Deno9

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [t-chen](https://github.com/tepel-chen/)                                                    |
| **Category** | rev                                                                                         |
| **Solves**   | 1                                                                                           |
| **Files**    | [deno9.zip](./deno9.zip)                                                                    |

## Hints

### Hint 1

“+” ← Does this look like an addition operator to you? Hmm… maybe it’s tricking you.

# Solution

You can run

```bash
sqlite3 v8_code_cache_v2 "SELECT hex(data) FROM codecache" | xxd -r -p > ./cache_orig.bin
```

to extract the v8 cache. Also you can run:

```bash
deno run --v8-flags=--print-bytecode main.ts
```

to run the script and output bytecode. From there, you can deduce the meaning of opcodes and the meaning of operands.

Create a disassembler and recover the true numbers.

See `solve.py` for the full script.
