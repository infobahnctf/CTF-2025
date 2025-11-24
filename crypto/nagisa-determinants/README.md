<img src="https://i.postimg.cc/SxLj59m6/Nagisa-Determinants.webp" alt="Nagisa Determinants" height="500">

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [Aeren](https://github.com/Aeren1564)                                                       |
| **Category** | crypto                                                                                      |
| **Solves**   | 3                                                                                           |
| **Files**    | [challenge.py](./challenge.py), [outputs.zip](./outputs.zip)                                |

# Solution

Consider $i$-th output, where $0 \le i < 300$.

Let $G[i]$ be a graph over $8$ vertices $0, 1, \cdots, 7$ where first $8$ pairs of $pos$ denotes its edges, and $key$ denotes each edge's weight.

Because $pos$ has no duplicate pairs or a pair with same values, $G[i]$ is simple.

$S$ denotes its adjacency matrix, ignoring weights, and the trace of $S^3$ is the number of triangles in $G$, times 6.

Determinant of $O$ denotes the $(3, 3)$-cofactor of the laplacian matrix of $G$. By Kirchhoff's theorem,

$$ \text{Det}(O) = \sum\_{T \text{ is a spanning tree of } G[i]} \text{Weight}(T) \mod p $$

where $\text{Weight}(T)$ is the product of weights of edges in $T$.

Since each output is non-zero, $G[i]$ has at least one spanning tree, and thus it is connected.

Note that each spanning tree excludes exactly two edges.

For $0 \le u < v < 8$, let $W_{u,v}$ denotes the product of all $key$ except for $key[u]$ and $key[v]$, modulo $p$.

Then $\text{Weight}(T) = W_{u, v}$ where $key[u]$ and $key[v]$ are the weight of the excluded edges.

Each spanning tree of a graph excludes different pair of edges. Therefore,

$$\text{Det}(O) = \left( \sum_{0 \le u < v < 8} b_{i,u,v} W_{u,v} \right) - k_i \cdot p$$

where $0 \le b_{i,u,v} < 2$ and $0 \le k_i < 28$. We can now recover $b_{i,u,v}$ with orthogonal lattice.

Author's lattice never fully recovered all $b_{i,u,v}$, and different heuristics for recovering last few incorrect $b_{i,u,v}$ gave different success rate of recovering answer.

Currently, the solver tries up to $3$ correctly recovered vectors, and add/subtract them to incorrect vectors. This heuristic works on 19 out of 24 given outputs.

After recovering $b_{i, u, v}$, we just have to check if $\sum_{0 \le u < v < 8} b_{i, u, v} \in \lbrace 8, 9 \rbrace$ to see if the number of triangles is $2$.

[Implementation](./solution.py)
