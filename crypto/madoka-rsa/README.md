<img src="https://i.postimg.cc/kgfDH7Jx/Madoka-RSA.webp" alt="Madoka RSA" height="500">

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [Aeren](https://github.com/Aeren1564)                                                       |
| **Category** | crypto                                                                                      |
| **Solves**   | 3                                                                                           |
| **Files**    | [challenge.py](./challenge.py), [output.txt](./output.txt)                                  |

# Solution

Let $b$, $u$, and $v$ be integers such that

- $q = u^2 + 3v^2$ is a prime congruent to $1$ modulo $3$,
- $1 \le b < q$ and $b$ is a cubic residue (modulo $q$), and
- remainder of $u$ modulo $3$ is 1 if and only if $b$ is a quadratic residue.

Then, by the Deuring's theorem, the elliptic curve $E_q:Y^2=X^3+b$ over $\mathbb{F}_ q$ is of order $q+1-2u$.

We obtain parameters in the challenge by setting $b=1$, $u=-2$, and $v=2x+1$, and the order of $E_q$ is $q+5=12p$.

Let $E_p$ be the elliptic curve $Y^2=X^3+1$ over $\mathbb{Z}/p\mathbb{Z}$, and $E_n$ be the direct product of $E_p$ and $E_q$. We can represent each coordinate with CRT.

There is a natural homomorphism $\phi:E_n \rightarrow E_q$ defined by $(x : y : z) \mapsto (x \mod q : y \mod q : z \mod q)$.

Let $G=(1 : \sqrt{2} : 1)$ be a point in $E_n$. Then

$$\phi(12 n G) = 12 p \cdot \phi(q r  G) = (0 : 1 : 0)$$

Therefore, the $Z$-coordinate of $12 n G$ is a multiple of $q$, and we can recover $q$ by computing GCD with $n$.

[Implementation](./solution.py)

# Alternative Solution

While I set this challenge, I noticed that $(2, 3)$, $(2, -3)$, $(0, 1)$, and $(0, -1)$ are the only rational points on $Y^2=X^3+1$ over $\mathbb{Q}$, and they all have very small order, so it's impossible to construct non-trivial base point without factorizing $n$.

I incorrectly assumed that this would be true for arbitrary choice of $b$ and concluded that $\sqrt{2}$ hint is needed, but after the contest, discord user @neobeo mentioned that $b=8$ with base point $(2, 4)$ works without $\sqrt{2}$ hint. (Note that $8$ is always a quadratic residue because $2$ is a quadratic residue)
