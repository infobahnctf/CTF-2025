import random

b = 256
m = 2 * b
n = 6 * m
"""
<b> (b) (2 * b) (b) <b>
"""

p = list(range(n))
for i in range(n):
	if random.randrange(2):
		p[i] = ~i
random.shuffle(p)

edge = [[] for _ in range(n)]

def orient(u, v):
	ru, rv = max(u, ~u), max(v, ~v)
	edge[abs(ru - rv)].append((u, v))

scc = [[p[i]] for i in range(n // 2)]
for i in range(n // 2, n):
	scc[random.randrange(n // 2)].append(p[i])

for i in range(len(scc)):
	if len(scc[i]) >= 2:
		for j in range(len(scc[i])):
			u, v = scc[i][j], scc[i][(j + 1) % len(scc[i])]
			orient(u, v)
		for _ in range(10):
			while True:
				u, v = random.choice(scc[i]), random.choice(scc[i])
				if u != v:
					orient(u, v)
					break

group = [[] for _ in range(b + 3)]
for i in range(b):
	group[i] += scc[i]
for i in range(b, 2 * b):
	group[b + 0] += scc[i]
for i in range(2 * b, 4 * b):
	group[b + 1] += scc[i]
for i in range(4 * b, 5 * b):
	group[b + 2] += scc[i]
for i in range(5 * b, 6 * b):
	group.append(scc[i][:])
assert max(len(group[b]), len(group[b + 2]) <= len(group[b + 1]))

def orient_group(i, j):
	assert i != j
	orient(random.choice(group[i]), random.choice(group[j]))

for i in range(b):
	orient_group(i, i + 1)
for i in range(b + 3, 2 * b + 3):
	orient_group(i - 1, i)
for i in range(len(group[b])):
	orient(random.choice(group[random.randrange(b)]), group[b][i])
	orient(group[b][i], group[b + 1][i])
	orient(group[b][i], group[b + 1][len(group[b + 1]) - len(group[b]) + i])
for i in range(len(group[b + 1])):
	orient(random.choice(group[b]), group[b + 1][i])
	orient(group[b + 1][i], random.choice(group[b + 2]))
for i in range(len(group[b + 2])):
	orient(group[b + 1][i], group[b + 2][i])
	orient(group[b + 1][len(group[b + 1]) - len(group[b + 2]) + i], group[b + 2][i])
	orient(group[b + 2][i], random.choice(group[random.randrange(b + 3, b + 3 + b)]))
group_id = {}
group_index = {}
for i in range(len(group)):
	for index, u in enumerate(group[i]):
		group_id[u] = i
		group_index[u] = index
for _ in range(30 * n):
	while True:
		u, v = p[random.randrange(n)], p[random.randrange(n)]
		uid, vid = group_id[u], group_id[v]
		if uid < vid and (not (b <= uid <= b + 2) or not (b <= vid <= b + 2)):
			orient(u, v)
			break

with open("key.txt", "w") as file:
	file.write(str(n) + " " + str(m) + "\n")
	lines = []
	for shift in range(1, n):
		if len(edge[shift]) == 0:
			continue
		offset_0_0 = 0 # smaller index
		offset_1_0 = 0 # bigger index
		bit_select_0 = 0
		offset_0_1 = 0 # smaller index
		offset_1_1 = 0 # bigger index
		bit_select_1 = 0
		for u, v in edge[shift]:
			ru, rv = max(u, ~u), max(v, ~v)
			u = ~u
			if ru > rv:
				ru, rv = rv, ru
				u, v = v, u
			assert rv - ru == shift
			if bit_select_0 >> ru & 1:
				if not (offset_0_0 >> ru & 1 == (1 if u < 0 else 0) and offset_1_0 >> rv & 1 == (1 if v < 0 else 0)):
					if bit_select_1 >> ru & 1:
						assert offset_0_1 >> ru & 1 == (1 if u < 0 else 0)
						assert offset_1_1 >> rv & 1 == (1 if v < 0 else 0)
					else:
						bit_select_1 |= 1 << ru
						if u < 0:
							offset_0_1 |= 1 << ru
						if v < 0:
							offset_1_1 |= 1 << rv
			else:
				bit_select_0 |= 1 << ru
				if u < 0:
					offset_0_0 |= 1 << ru
				if v < 0:
					offset_1_0 |= 1 << rv
		if bit_select_0:
			lines.append(" ".join([str(shift), str(offset_0_0), str(offset_1_0), str(bit_select_0)]))
		if bit_select_1:
			lines.append(" ".join([str(shift), str(offset_0_1), str(offset_1_1), str(bit_select_1)]))
	random.shuffle(lines)
	file.write("\n".join(lines))
