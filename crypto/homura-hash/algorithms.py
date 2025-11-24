class two_sat_solver:
	def __init__(self, n):
		self.n = n
		self.adj = [[] for _ in range(2 * n)]
		self.value = []
	def add_variable(self):
		self.adj.append([])
		self.adj.append([])
		self.n += 1
		return self.n - 1
	def either(self, u, v):
		u = max(2 * u, -1 - 2 * u)
		v = max(2 * v, -1 - 2 * v)
		self.adj[u].append(v ^ 1)
		self.adj[v].append(u ^ 1)
	def implies(self, u, v):
		self.either(~u, v)
	def equals(self, u, v):
		self.either(~u, v)
		self.either(u, ~v)
	def differs(self, u, v):
		self.either(u, v)
		self.either(~u, ~v)
	def set_value(self, u, x = True):
		if x:
			self.either(u, u)
		else:
			self.either(~u, ~u)
	def at_most_one(self, arr):
		if len(arr) <= 1:
			return
		cur = ~arr[0]
		for i in range(2, len(arr)):
			next_var = self.add_variable()
			self.either(cur, ~arr[i])
			self.either(cur, next_var)
			self.either(~arr[i], next_var)
			cur = ~next_var
		self.either(cur, ~arr[1])
	def _dfs(self, u):
		self.time += 1
		low = self.time
		self.val[u] = self.time
		self.z.append(u)
		for v in self.adj[u]:
			if self.comp[v] == -1:
				if self.val[v] == 0:
					low = min(low, self._dfs(v))
				else:
					low = min(low, self.val[v])
		self.time += 1
		if low == self.val[u]:
			while True:
				v = self.z.pop()
				self.comp[v] = self.comp_cnt
				if self.value[v >> 1] == -1:
					self.value[v >> 1] = v & 1
				if v == u:
					break
			self.comp_cnt += 1
		self.val[u] = low
		return low
	def solve(self):
		self.value = [-1] * self.n
		self.val = [0] * (2 * self.n)
		self.comp = [-1] * (2 * self.n)
		self.z = []
		self.time = 0
		self.comp_cnt = 0
		for u in range(2 * self.n):
			if self.comp[u] == -1:
				self._dfs(u)
		for u in range(self.n):
			if self.comp[u << 1] == self.comp[u << 1 ^ 1]:
				return False
		return True

class flow_network:
	class Edge:
		def __init__(self, from_, to, capacity, flow):
			self.from_ = from_
			self.to = to
			self.capacity = capacity
			self.flow = flow
		def saturated(self):
			eps = 0
			return self.capacity - self.flow <= eps
	def __init__(self, n: int):
		self.n = n
		self.adj = [[] for _ in range(n)]
		self.edge = []
	def orient(self, from_: int, to: int, cap: int) -> int:
		assert 0 <= min(from_, to) and max(from_, to) < self.n and cap >= 0
		ind = len(self.edge)
		self.adj[from_].append(ind)
		self.edge.append(self.Edge(from_, to, cap, 0))
		self.adj[to].append(ind + 1)
		self.edge.append(self.Edge(to, from_, 0, 0))
		return ind
	def add_flow(self, i: int, f: int):
		self.edge[i].flow += f
		self.edge[i ^ 1].flow -= f

class dinic_maximum_flow:
	def __init__(self, F):
		assert isinstance(F, flow_network)
		self.eps = 0
		self.inf = 10**18
		self.F = F
		self.ptr = [0] * F.n
		self.level = [0] * F.n
		self.q = [0] * F.n
	def bfs(self, source: int, sink: int) -> bool:
		self.level = [-1] * self.F.n
		self.q[0] = sink
		self.level[sink] = 0
		beg, end = 0, 1
		while beg < end:
			i = self.q[beg]
			beg += 1
			for ind in self.F.adj[i]:
				e = self.F.edge[ind]
				re = self.F.edge[ind ^ 1]
				if re.capacity - re.flow > self.eps and self.level[e.to] == -1:
					self.level[e.to] = self.level[i] + 1
					if e.to == source:
						return True
					self.q[end] = e.to
					end += 1
		return False
	def _dfs(self, u: int, w: int, sink: int) -> int:
		if u == sink:
			return w
		while self.ptr[u] >= 0:
			ind = self.F.adj[u][self.ptr[u]]
			e = self.F.edge[ind]
			if e.capacity - e.flow > self.eps and self.level[e.to] == self.level[u] - 1:
				flow = self._dfs(e.to, min(e.capacity - e.flow, w), sink)
				if flow > self.eps:
					self.F.add_flow(ind, flow)
					return flow
			self.ptr[u] -= 1
		return 0
	def maximum_flow(self, source: int, sink: int) -> int:
		assert 0 <= source < self.F.n and 0 <= sink < self.F.n
		flow = 0
		while self.bfs(source, sink):
			for i in range(self.F.n):
				self.ptr[i] = len(self.F.adj[i]) - 1
			while True:
				add = self._dfs(source, self.inf, sink)
				if add <= self.eps:
					break
				flow += add
		return flow

def maximum_antichain(n, edge, vertex_weight = []):
	assert n >= 1
	if not vertex_weight:
		vertex_weight = [1] * n
	assert min(vertex_weight) >= 0
	F = flow_network(2 * n + 2)
	idL = [0] * n
	idR = [0] * n
	for u in range(n):
		idL[u] = F.orient(2 * n, u, vertex_weight[u])
		idR[u] = F.orient(n + u, 2 * n + 1, vertex_weight[u])
	for u, v in edge:
		F.orient(u, n + v, 10**18)
	dinic_maximum_flow(F).maximum_flow(2 * n, 2 * n + 1)
	vis = [False] * (2 * n)
	def _dfs(u: int):
		vis[u] = True
		for id in F.adj[u]:
			v = F.edge[id].to
			if v >= 2 * n or vis[v]:
				continue
			if u < n:
				if (F.edge[idL[u]].saturated() and
					F.edge[idR[v - n]].saturated() and
					F.edge[idL[u]].flow == F.edge[id].flow and
					F.edge[id].flow == F.edge[idR[v - n]].flow):
					continue
			elif F.edge[id].flow == 0:
				continue
			_dfs(v)
	for u in range(n):
		if not vis[u] and not F.edge[idL[u]].saturated():
			_dfs(u)
	antichain = [u for u in range(n) if vis[u] and not vis[n + u]]
	return antichain

class disjoint_set:
	def __init__(self, n):
		self.n = n
		self.p = [-1] * self.n
		self._group_count = n
	def root(self, u):
		if self.p[u] < 0:
			return u
		self.p[u] = self.root(self.p[u])
		return self.p[u]
	def size(self, u):
		return -self.p[self.root(u)]
	def share(self, u, v):
		return self.root(u) == self.root(v)
	def merge(self, u, v):
		u, v = self.root(u), self.root(v)
		if u == v:
			return False
		if self.p[u] > self.p[v]:
			u, v = v, u
		self.p[u] += self.p[v]
		self.p[v] = u
		self._group_count -= 1
		return True
	def clear(self):
		self.p = [-1] * self.n
		self._group_count = self.n
	def group_count(self):
		return self._group_count
	def group_up(self):
		group = [[] for _ in range(self.n)]
		for i in range(self.n):
			group[self.root(i)].append(i)
		return [g for g in group if len(g) > 0]

def pick_subset_with_given_xor(values : list, target : int):
	from sage.all import GF, matrix, vector
	values, target = list(map(int, values)), int(target)
	assert all(x >= 0 for x in values) and target >= 0
	dim = target.bit_length()
	for x in values:
		dim = max(dim, x.bit_length())
	mat = []
	for d in range(dim):
		row = []
		for i, x in enumerate(values):
			row.append(x >> d & 1)
		mat.append(row)
	try:
		res = matrix(GF(2), mat).solve_right(vector(GF(2), [target >> i & 1 for i in range(dim)]))
	except:
		return None
	s = 0
	for i, x in enumerate(values):
		if res[i]:
			s ^= x
	assert s == target
	return [i for i in range(len(res)) if res[i]]
