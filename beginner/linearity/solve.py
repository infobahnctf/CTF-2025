from collections import defaultdict
import hashlib, string

V = [14, 38, 56, 76, 51]
C = [1357,2854,1102,1723,4416,283,344,4566,5023,1798,477,3833,1839,5416,4017,1066,161,415,5637,1696,1058,3025,5286,5141,3818,1373,2839,1102,1764,4432,313,322,4545,5012,1835,477,3825]
TARGET = "e256693b7b7d07e11f2f83f452f04969ea327261d56406d2d657da1066cefa17"

alphabet = set(string.ascii_letters + string.digits + "_{}")

cells = defaultdict(list)
for i in range(len(C)):
    cells[((i//5)%5, i%5)].append(i)

def valid_candidates(v, idxs):
    good = []
    for m in range(101):
        val = v * m
        chars, ok = [], True
        for i in idxs:
            chv = C[i] ^ val
            if not (32 <= chv <= 126) or chr(chv) not in alphabet:
                ok = False
                break
            chars.append(chr(chv))
        if ok:
            good.append(tuple(chars))
    return good

cell_items = sorted((cell, valid_candidates(V[cell[1]], idxs)) for cell, idxs in cells.items())
pos = [''] * len(C)
prefix = "infobahn{"

def dfs(i=0):
    if i == len(cell_items):
        cand = ''.join(pos)
        if hashlib.sha256(cand.encode()).hexdigest() == TARGET:
            print(cand)
            return True
        return False
    cell, poss = cell_items[i]
    for chars in poss:
        ok = True
        for j, ch in zip(cells[cell], chars):
            if (j < len(prefix) and ch != prefix[j]) or (j == len(C)-1 and ch != '}') or (pos[j] and pos[j] != ch):
                ok = False
                break
        if not ok:
            continue
        changed = [j for j, ch in zip(cells[cell], chars) if not pos[j]]
        for j, ch in zip(cells[cell], chars):
            if not pos[j]:
                pos[j] = ch
        if dfs(i+1):
            return True
        for j in changed:
            pos[j] = ''

dfs()
