<img src="https://i.postimg.cc/0Q2htrRt/Homura-Hash.webp" alt="Homura Hash" height="500">

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [Aeren](https://github.com/Aeren1564)                                                       |
| **Category** | crypto                                                                                      |
| **Solves**   | 1                                                                                           |
| **Files**    | [challenge/server.py](./challenge/server.py), [key.txt.zip](./key.txt.zip)                  |

# Solution

The goal is to find a subset of $\lbrace x: HH(x)=0 \rbrace$ which forms a vector/affine space over $\mathbb{F}_ 2$ of large dimension.

The condition $HH(x)=0$ defines a 2SAT equation on the individual bits of $x$.

Construct the implication graph $G$ for the 2SAT equation. Since each vertices inside a strongly connected component must be assigned to the same value, we can replace each component with a new variable.

A solution to the 2SAT equation is equivalent to a partition of vertices of $G$ into two sets $L$ and $R$ so that there is no path starting in $R$ and ending in $L$.

Now, to construct a large vector/affine space, we should find an antichain $C$ in $G$. We can assign every vertex which can reach $C$ to true, and remaining vertices to false, and then we are allowed to freely assign each vertex in $C$ to true or false.

This generates an affine space of dimension equal to the size of $C$, and the largest of them can be found to be $512$ which gives $1/2$ chance to correctly answer on each connection.

Finding an antichain of maximum size is a known problem which can be solved in polynomial time.

[Implementation](./solution.py)
