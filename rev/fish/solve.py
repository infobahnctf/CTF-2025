from functools import reduce
from tqdm import tqdm
res = 1
multis = [1, 2, 3, 4, 5]
prods = reduce(lambda x,y:x*y, multis)
for i in tqdm(range(1, 15**8)):
    if i % (prods+1) == 0:
        pos = (i % 13) % 5
        val = (i % 15) + 1
        multis[pos] = val
        prods = reduce(lambda x,y:x*y, multis)
        res += i

print(res)
val = res * 13245360976512853488898773238998 + 161889635703666
while val > 0:
    print(chr((val % 96) + 0x20), end='')
    val = val // 96
print()