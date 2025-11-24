import math
import random
flag = "infobahn{l1ttL3_d1D_I_Know_th47_d3no_D3pend5_0n_sQL1t3}"

def closest_factors(n: int):
    root = int(math.isqrt(n))
    for a in range(root, 1, -1):
        if n % a == 0:
            b = n // a
            return a, b
    return None, None
res = []
var = {}
for c in flag:
    l = ord(c)*5+3
    a = list(range(100))
    random.shuffle(a)
    for x in a:
        aa, bb = closest_factors(l - x)
        if not aa or not bb:
            continue
        if random.randint(0, 1) == 0:
            aa, bb = bb, aa
        if aa not in var:
            var[aa] = "v0v{:02}".format(len(var))
        if bb not in var:
            var[bb] = "v0v{:02}".format(len(var))
        if x not in var:
            var[x] = "v0v{:02}".format(len(var))
        if random.randint(0, 1) == 0:
            res.append(f"{var[aa]}*{var[bb]}+{var[x]}")
        else:
            res.append(f"{var[x]}+{var[aa]}*{var[bb]}")
        break
out = '[' + ','.join(res) + ']'
print(out)
keys = list(var.keys())
random.shuffle(keys)
print('[' + ",".join([var[v] for v in keys]) + ']=[' + ",".join(["{:d}^v0004".format(v ^ ord('i')) for v in keys]) + ']')
# print("".join([chr((r-3)//5) for r in eval(out)]))
