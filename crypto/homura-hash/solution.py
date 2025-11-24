from Crypto.Cipher import AES
import hashlib
from pwn import *
from algorithms import two_sat_solver, maximum_antichain, disjoint_set, pick_subset_with_given_xor

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

antichain = maximum_antichain(tss.comp_cnt, edge)
for u in antichain:
	for v in antichain:
		if u != v:
			assert ~reachable[u] >> v & 1 and ~reachable[v] >> u & 1

dsu = disjoint_set(tss.comp_cnt)
for i in range(tss.comp_cnt):
	for u in has[i]:
		for v in tss.adj[u]:
			dsu.merge(tss.comp[u], tss.comp[v])

antichain = [i for i in antichain if dsu.share(0, i)]
antichain_mask = 0
for i in antichain:
	antichain_mask |= 1 << i
base = 0
for i in range(tss.comp_cnt):
	if not dsu.share(0, i) or i in antichain:
		continue
	for u in has[i]:
		if u & 1 == (1 if reachable[i] & antichain_mask == 0 else 0):
			base |= 1 << u // 2

while True:
	with process(["python3", "challenge/server.py"]) as io:
		goal = int(io.readlineS().strip())
		query = []
		for focus in range(len(antichain)):
			x = base
			for t, i in enumerate(antichain):
				for u in has[i]:
					if u & 1 == (0 if t == focus else 1):
						x |= 1 << u // 2
			query.append(x)
		io.readuntil(b"QUERY> ")
		io.sendline(" ".join(map(str, query)).encode())
		ans = list(map(int, io.readlineS().strip().split(" ")))
		subset = pick_subset_with_given_xor(ans, goal)
		if subset == None or len(subset) % 2 == 0:
			print(f"Subset size is even, retrying")
			continue
		x = base
		for t, i in enumerate(antichain):
			for u in has[i]:
				if u & 1 == (0 if t in subset else 1):
					x |= 1 << u // 2
		io.readuntil(b"ANSWER> ")
		io.sendline(str(x).encode())
		print(io.readallS(timeout = 1).strip())
		break
