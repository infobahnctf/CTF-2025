<img src="https://i.postimg.cc/XYyhhwyx/Kyoko-Ring.webp" alt="Kyoko Ring" height="500">

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [Aeren](https://github.com/Aeren1564)                                                       |
| **Category** | crypto                                                                                      |
| **Solves**   | 7                                                                                           |
| **Files**    | [challenge.py](./challenge.py), [output.txt](./output.txt)                                  |

# Solution

Let $G$ be the multiplicative group in the challenge.

Note that $G$ is a direct product of $G_p$ and $G_q$, where $G_p$ is the "modulo $p$" part, and $G_q$ is the "modulo $q$" part. So we can solve DLOG independently in $G_p$ and $G_q$ and merge the result with CRT. Furthermore, $G_p$ and $G_q$ are diagonal-wise reflection of each other, so we can apply the same method to solve DLOG. Therefore, we'll only consider $G_p$.

The value at $(i, j)$ can be uniquely expressed as an integer in range $[0, p^{i + 1 - \max(0, i - j)})$ multiplied by $p^{\max(0, i - j)}$.

Let $H_p$ be the group where the value at $(i, j)$ is an integer in range $[0, p)$ multiplied by $p^{\max(0, i - j)}$.

There is a natural homomorphism $\phi_p: G_p \rightarrow H_p$ defined by $a \mapsto b$ where $b[i,j] = a[i,j] \mod p^{\max(0, i - j) + 1}$.

Our goal is to find $x$ with $g^x=h$, given $g, h \in G_p$.

We start by finding $x \mod \text{ord}(\phi_p(g))$, which is just finding $y$ with $\phi_p(g)^y = \phi_p(h)$.

Due to structure of $H_p$, we can verify with some simple computation that the lower triangular part of each element of $H_p$ acts independently to the upper triangular part. Therefore, we merely have to solve DLOG for triangular matrix, which is just solving DLOG for each diagonal elements.

Now we ignore the $\text{ord}(\phi_p(g))$ part by replacing $g$ and $h$ with $g^{\text{ord}(\phi_p(g))}$ and $h^{\text{ord}(\phi_p(g))}$.

We can again verify that the multiplication between resulting elements have upper and lower triangular part acting independently, hence the DLOG again can be found by DLOG on diagonal elements.

[Implementation](./solution.py)

# Alternative Solution

Discord user @helllman has mentioned that one of the eigenvalues of the matrix, treating it as $\mathbb{Z}/p^3\mathbb{Z}$ matrix, works as intended, and we merely have to try each pair of eigenvalues and compute DLOG over $\mathbb{Z}/p^3\mathbb{Z}$.
