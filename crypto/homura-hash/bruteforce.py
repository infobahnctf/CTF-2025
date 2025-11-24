from CTF_Library import *

with open("key.txt") as file:
	n, m = map(int, file.readline().strip().split(" "))
	tss = two_sat_solver(n)
	key = []
	for line in file.read().split("\n"):
		shift, offset_0, offset_1, bit_select = list(map(int, line.split(" ")))
		for bit in range(n):
			if bit_select >> bit & 1:
				assert bit + shift < n
				u, v = ~bit, ~(bit + shift)
				if offset_0 >> bit & 1:
					u = ~u
				if offset_1 >> bit + shift & 1:
					v = ~v
				tss.either(u, v)
		key.append([shift, offset_0, offset_1, bit_select])

assert tss.solve()

has = [[] for _ in range(tss.comp_cnt)]
reachable = [0] * tss.comp_cnt
for u in range(2 * n):
	has[tss.comp[u]].append(u)
vis = [-1] * tss.comp_cnt
for t in range(tss.comp_cnt):
	vis[t] = t
	reachable[t] |= 1 << t
	for u in has[t]:
		for v in tss.adj[u]:
			if vis[tss.comp[v]] != t:
				vis[tss.comp[v]] = t
				reachable[t] |= reachable[tss.comp[v]]
edge = [(u, v) for u in range(tss.comp_cnt) for v in range(tss.comp_cnt) if u != v and reachable[u] >> v & 1]

dsu = disjoint_set(tss.comp_cnt)
for i in range(tss.comp_cnt):
	for u in has[i]:
		for v in tss.adj[u]:
			dsu.merge(tss.comp[u], tss.comp[v])

import random
comp = [i for i in range(tss.comp_cnt) if dsu.share(0, i)]
opt = 0
while True:
	order = comp[:]
	random.shuffle(order)
	chain = []
	for i in order:
		if all(~reachable[i] >> j & 1 and ~reachable[j] >> i & 1 for j in chain):
			chain.append(i)
	opt = max(opt, len(chain))
	print(f"{len(chain) = }")
	print(f"{opt = }")
	print()
	if len(chain) == m:
		break
