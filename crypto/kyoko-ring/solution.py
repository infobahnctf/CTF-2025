import ast
from Crypto.Cipher import AES
from Crypto.Util.number import isPrime
import hashlib
from sage.all import *
from challenge import Kyoko_Ring

with open("output.txt") as file:
	g = ast.literal_eval(file.readline())
	h = ast.literal_eval(file.readline())
	enc_flag = bytes.fromhex(file.readline())
	p = gcd(g[1][0], gcd(g[2][0], g[2][1]))
	q = gcd(g[0][1], gcd(g[0][2], g[1][2]))
	for x in range(2, 100000):
		while p % x == 0:
			p //= x
		while q % x == 0:
			q //= x
	assert isPrime(p) and isPrime(q)

rems, ords = [], []
for _ in range(2):
	Fp = GF(p)

	rems += [Fp(h[i][i]).log(Fp(g[i][i])) for i in range(3)]
	ords += [Fp(g[i][i]).multiplicative_order() for i in range(3)]

	x = Kyoko_Ring(p, q, g)**lcm([Fp(g[i][i]).multiplicative_order() for i in range(3)])
	y = Kyoko_Ring(p, q, h)**lcm([Fp(g[i][i]).multiplicative_order() for i in range(3)])
	R = Zmod(p**3)
	rems.append(int(R(y.data[2][2]).log(R(x.data[2][2]))))
	ords.append(R(x.data[2][2]).multiplicative_order())

	p, q = q, p
	g = [[g[j][i] for j in range(3)] for i in range(3)]
	h = [[h[j][i] for j in range(3)] for i in range(3)]

secret = CRT(rems, ords)

print(AES.new(hashlib.sha256(hex(secret).encode()).digest()[:16], AES.MODE_ECB).decrypt(enc_flag))
