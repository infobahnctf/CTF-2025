<img src="https://i.postimg.cc/PJDXhhTS/Mami-LES.webp" alt="Mami LES" height="500">

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [Aeren](https://github.com/Aeren1564)                                                       |
| **Category** | crypto                                                                                      |
| **Solves**   | 1                                                                                           |
| **Files**    | [challenge/server.py](./challenge/server.py)                                                |

# Solution

The intended solution only uses decryption.

We can represent decryption as

$$
\begin{aligned}
&\left( \sum_{i=0}^{99} \text{ciphertext}[i] \cdot \left( \text{secret} + i \right)^{-1500} \cdot X^i \right) \left( \prod_{j=1}^{99} (1-X^j) \right) \mod X^{100} \\
&= \left( \sum_{i=0}^{99} \text{ciphertext}[i] \cdot \left( \text{secret} + i \right)^{-1500} \cdot X^i \right) \\
&\left( 1 - X - X^2 + X^5 + X^7 - X^{12} - X^{15} + X^{22} + X^{26} - X^{35} - X^{40} + X^{51} + X^{57} - X^{70} - X^{77} + X^{92} \right) \mod X^{100}
\end{aligned}
$$

(If you would like to know why the polynomial at the end is so sparse, search pentagonal number theorem)

We would like to avoid padding entirely. This can be achieved at index $91$ by sandwiching the padding part between $X^{77}$ and $X^{92}$.

We'll only send lists of length $50$ consisting of a single value $v$. When we query with the same $v$ $1000$ times, the probability that the padding gets avoided by output index $91$ at least once is

$$
\begin{aligned}
1-\left( 1 - \frac{\binom{71}{35}}{\binom{86}{50}} \right)^{1000} \approx 0.09817073
\end{aligned}
$$

We'll query with $v=1$, $1000$ times, and then with $v=9$, $1000$ times. We try all $1000^2$ pairs, and assume both output avoided all paddings at index $91$, and recover $p$ and $\text{secret}$ with elementary method.

This method is expected to work in $1/0.09817073^2 \approx 104$ connections on average.

Here, it might be very slow to check all possible $p$. We can optimize this using the fact that the distribution of the maximum of uniformly and independently distributed $n$ real variables over the interval $[0, 1]$ has average value $n/(n+1)$. Let $L$ be the maximum of all values in the query, and $R=1.00005 \cdot L$. Then the actual $p$ almost always lies in the interval $[L, R]$ while the fake $p$s we're checking almost never lies in that range.

[Implementation](./solution.py)
