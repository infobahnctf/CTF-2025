from Crypto.Cipher import AES
import hashlib
import itertools
# https://github.com/Aeren1564/CTF_Library/blob/master/CTF_Library/Cryptography/MersenneTwister/python_random_breaker.py
from CTF_Library import python_random_breaker

n = 42
with open("output.txt") as file:
	stream = int(file.readline().strip(), 16)
	enc_flag = bytes.fromhex(file.readline().strip())

def index(x, y, z):
	return n * n * x + n * y + z

def solve(z, xlast, ylast):
	print(f"{z = }, {xlast = }, {ylast = }")
	global stream
	plane = [
		[
			stream >> index(x, y, z) & 1
			for y in range(n)
		]
		for x in range(n)
	]
	if xlast ^ ylast ^ plane[n - 1][n - 1] == 0:
		return
	plane[n - 1][n - 1] = 1
	xflip, yflip = [0] * n, [0] * n
	xflip[n - 1] = xlast
	yflip[n - 1] = ylast
	for x in range(n - 1):
		if plane[x][n - 1] == 0:
			plane[x][n - 1] = xflip[x] = 1
	for y in range(n - 1):
		if plane[n - 1][y] == 0:
			plane[n - 1][y] = yflip[y] = 1
	for x in range(n - 1):
		for y in range(n - 1):
			if xflip[x] ^ yflip[y]:
				plane[x][y] ^= 1
	for x in range(n - 1):
		cnt = sum(1 - plane[x][y] for y in range(n))
		if 2 * cnt >= n:
			xflip[x] ^= 1
	for y in range(n - 1):
		cnt = sum(1 - plane[x][y] for x in range(n))
		if 2 * cnt >= n:
			yflip[y] ^= 1
	plane = [
		[
			stream >> index(x, y, z) & 1 ^ xflip[x] ^ yflip[y]
			for x in range(n)
		]
		for y in range(n)
	]
	for x in range(n):
		cnt = sum(1 - plane[x][y] for y in range(n))
		if 4 * cnt >= n:
			return
	for y in range(n):
		cnt = sum(1 - plane[x][y] for x in range(n))
		if 4 * cnt >= n:
			return
	cube = [
		[
			[
				stream >> index(x, y, z) & 1 ^ xflip[x] ^ yflip[y]
				for z in range(n)
			]
			for y in range(n)
		]
		for x in range(n)
	]
	zflip = [0] * n
	for z in range(n):
		cnt = sum(1 - cube[x][y][z] for x in range(n) for y in range(n))
		if 2 * cnt >= n * n:
			zflip[z] ^= 1
			for x in range(n):
				for y in range(n):
					cube[x][y][z] ^= 1
	print(f"{xflip = }")
	print(f"{yflip = }")
	print(f"{zflip = }")
	stream = 0
	for x in range(n):
		for y in range(n):
			for z in range(n):
				stream ^= cube[x][y][z] << index(x, y, z)
	zero_ratio = 1 - stream.bit_count() / n**3
	if zero_ratio > 7 / 32:
		return
	xcnt, ycnt, zcnt = [0] * n, [0] * n, [0] * n
	for x in range(n):
		for y in range(n):
			for z in range(n):
				if ~stream >> index(x, y, z) & 1:
					xcnt[x] += 1
					ycnt[y] += 1
					zcnt[z] += 1
	print(f"{xcnt = }")
	print(f"{ycnt = }")
	print(f"{zcnt = }")
	assert min(xcnt) > 0 and min(ycnt) > 0 and min(zcnt) > 0
	print(f"{32 * zero_ratio = }")
	breaker = python_random_breaker()
	breaker.init_twister_after_seeding()
	for _ in range(10**5 + 1024):
		breaker.setrandbits(5)
	for i in reversed(range(n**3)):
		if i % 10000 == 0:
			print(f"{i = }")
			print(f"{breaker.nullity() = }")
		eq = breaker.setrandbits(5)
		if ~stream >> i & 1:
			breaker.add_equation(eq[0][0] ^ eq[1][0], 1)
			breaker.add_equation(eq[0][0] ^ eq[2][0] ^ eq[3][0], 1)
			breaker.add_equation(eq[2][0] ^ eq[4][0], 1)
	for secret in breaker.recover_all_integer_seeds_from_state(breaker.recover_all_twister_states()[0], 19936):
		flag = AES.new(hashlib.sha256(hex(secret).encode()).digest()[:16], AES.MODE_ECB).decrypt(enc_flag)
		if flag.startswith(b"infobahn{"):
			print(f"{flag = }")
			exit()

for z, xlast, ylast in itertools.product(range(n), range(2), range(2)):
	solve(z, xlast, ylast)
