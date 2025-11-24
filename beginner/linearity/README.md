# Linearity

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [NeKroFR](https://github.com/NeKroFR)                                                       |
| **Category** | Beginner                                                                                    |
| **Solves**   | 382                                                                                         |
| **Files**    | [chall.py](chall.py)                                                                        |

# Description

A gentle introduction to linear cryptanalysis 🙂

# Solve

This challenge provides us a ciphertext where each bytes of the flag are xored with a value taken from a matrix `M`. The challenge gives us the vector `V` used to generate the matrix, the ciphertext `C`, and the sha256 hash of the flag.

The matrix cell used to mask a byte is determined by `row = (i // 5) % 5` and `col = i % 5`, so we have the same XOR mask repeated every 25 values. And because each cells are `V[col] * r` with a small `V[col]` and a random integer `r`, we can leak a linear structure.

To solve the challenge, we can just group ciphertext indices by their `(row, col)` cell so each group shares the same mask. Then, for each group we can bruteforce multipliers from 0 to 100, compute `val = V[col] * m`, xor it with every ciphertext in the group, and keep multiplier candidates which are valid ASCII. Then we just combine the candidates strings using DFS and compare candidates with the target hash.

You can check the solve script [here](./solve.py)
