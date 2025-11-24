from sage.all import *
from Crypto.Cipher import AES
import hashlib

with open("output.txt") as file:
	n = int(file.readline())
	e = int(file.readline())
	enc_key = int(file.readline())
	sqrt2 = int(file.readline())
	enc_flag = bytes.fromhex(file.readline())

EC = EllipticCurve(Zmod(n), [0, 1])
g = EC(1, sqrt2)
q = gcd(n, int(list(12 * n * g)[2]))
p = (q + 5) // 12
r = n // (p * q)
secret = pow(enc_key, pow(e, -1, (p - 1) * (q - 1) * (r - 1)), n)
print(AES.new(hashlib.sha256(hex(secret).encode()).digest()[:16], AES.MODE_ECB).decrypt(enc_flag))
