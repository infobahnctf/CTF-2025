import ast
from Crypto.Cipher import AES
from Crypto.Util.number import isPrime
import hashlib
from pwn import *
from sage.all import *
import time
proof.all(False)

penta = [0, 1, 2, 5, 7, 12, 15, 22, 26, 35, 40, 51, 57, 70, 77]

def compute_DF():
	X = ZZ['X'].gen()
	pref, suff = [1] * (len(penta) + 1), [1] * (len(penta) + 1)
	for i in range(len(penta)):
		pref[i + 1] = pref[i] * (X + 91 - penta[i])**1500
	for i in reversed(range(len(penta))):
		suff[i] = suff[i + 1] * (X + 91 - penta[i])**1500
	D = pref[-1]
	F = 0
	for i in range(len(penta)):
		F += pow(-1, i + 1 >> 1 & 1) * pref[i] * suff[i + 1]
	return D, F

start_time = time.time()
with open("DF.txt", "w") as file:
	D, F = compute_DF()
	file.write(
		" ".join(hex(x)[2:] if x >= 0 else "-" + hex(x)[3:] for x in list(D)) + "\n" +
		" ".join(hex(x)[2:] if x >= 0 else "-" + hex(x)[3:] for x in list(F)) + "\n"
	)
print("Logging finished in", time.time() - start_time)

with open("DF.txt", "r") as file:
	R = ZZ['X']
	D = R([int(x, 16) for x in file.readline().split(" ")])
	F = R([int(x, 16) for x in file.readline().split(" ")])

multiplier = 9
limit = 50
text = [
	" ".join("1" for _ in range(limit)).encode(),
	" ".join(str(multiplier) for _ in range(limit)).encode()
]

attempt = 0
while True:
	attempt += 1
	print(f"{attempt = }")
	batch = 500
	assert 500 % batch == 0
	with process(["python3", "challenge/server.py"]) as io:
		enc_flag = bytes.fromhex(io.readlineS().strip())
		cts = []
		lower_bound = 0
		for outer in range(2000 // batch):
			print(f"Batch #{outer}")
			for inner in range(batch):
				io.sendline(b"D")
				io.sendline(text[outer >= 1000 // batch])
			for inner in range(batch):
				io.readuntil(b"TEXT> ")
				cts.append([1] * 14 + ast.literal_eval(io.readlineS().strip()))
				lower_bound = max(lower_bound, max(*cts[-1]))
		upper_bound = int(1.00005 * lower_bound)
	for i in range(1000):
		x = multiplier * cts[i][91]
		for j in range(1000, 2000):
			p = x - cts[j][91]
			for d in reversed(range(2, multiplier + 1)):
				if p % d == 0:
					p //= d
					break
			if p.bit_length() == 512 and lower_bound < p <= upper_bound and isPrime(p):
				print(f"Matching found, {i = }, {j = }, {p = }")
				RXp, Xp = GF(p)['Xp'].objgen()
				Fp = RXp(F) - RXp(D) * cts[i][91]
				Fp = gcd(Fp, pow(Xp, p, Fp) - Xp)
				for secret in Fp.roots(multiplicities = False):
					flag = AES.new(hashlib.sha256(hex(secret).encode()).digest()[:16], AES.MODE_ECB).decrypt(enc_flag)
					if flag.startswith(b"infobahn{"):
						print(flag)
						exit()
				print()
