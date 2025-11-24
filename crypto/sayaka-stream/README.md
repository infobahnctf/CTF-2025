<img src="https://i.postimg.cc/02Qk3Hny/Sayaka-Stream.webp" alt="Sayaka Stream" height="500">

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [Aeren](https://github.com/Aeren1564)                                                       |
| **Category** | crypto                                                                                      |
| **Solves**   | 2                                                                                           |
| **Files**    | [challenge.py](./challenge.py), [output.txt](./output.txt)                                  |

# Solution

Over all $2^5=32$ possible ways to assign $a, b, c, d, e$, there are only $3$ assignments which outputs zero on "make_generator": $(0, 1, 0, 1, 1), (0, 1, 1, 0, 0), (1, 0, 0, 0, 1)$. Therefore, we expect zero with probability $3/32$.

We first separate stream and noise.

Take one of $3n$ planes arbitrarily, and iterate over all ways to flip the entire plane, along with the last row and the last column. We need to decide how to flip remaining $n-1$ rows and $n-1$ columns.

First, initialize the state of these $2(n-1)$ flips with the rule "last row and last column cells are all 1, except for the one cell at their intersection". Note that this uniquely determines the initial state of flips. Because we expect last row and column to have ones in the majority at the end, the true state of flip should differ very little from this. What this initialization does is that it minimizes the effect of flips in one direction have on flips in the other direction.

Now iterate over remaining $2(n-1)$ rows and columns. If zeroes are in the majority on that row/column, it's most likely that the current state of flip on that row/column must be changed, because this switch-of-majority most likely wasn't caused by flips in the other direction.

After deciding all $2(n-1)$ states like this, check if ones are in the majority in the entire grid. If so, we have successfully separated stream and noise.

Now, whenever we see a zero in the stream, we can extract three linear equations: $a \oplus b = 1$, $a \oplus c \oplus d = 1$, and $c \oplus e = 1$. (There are 8 possible linear equations but the rest are redundant) Using this, we can recover the internal state of MT, and after that, the initial seed.

[Implementation](./solution.py)
