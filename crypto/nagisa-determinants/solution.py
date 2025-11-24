import ast
from Crypto.Cipher import AES
import hashlib
import itertools
from sage.all import *
proof.all(False)

key_len = 8
weight_cnt = key_len * (key_len - 1) // 2

def orthogonal_complement_basis(vecs):
	assert len(set(len(v) for v in vecs)) == 1
	vecs = list(vector(ZZ, map(int, v)) for v in vecs)
	nv = len(vecs)
	base = [[matrix(ZZ, vecs).T, matrix.identity(ZZ, len(vecs[0]))]]
	L = block_matrix(ZZ, base)
	L[:, :nv] *= max([max(v) for v in vecs]) * 2**10
	L = L.LLL()
	return [vec[nv: ] for vec in L if vec[: nv] == 0]

cnt = [0, 0]
for file_id in range(24):
	print("attempt #" + str(file_id).zfill(2))

	with open("outputs/output" + str(file_id).zfill(2) + ".txt") as file:
		outputs = vector(ast.literal_eval(file.readline()))
		enc_flag = bytes.fromhex(file.readline())

	basis1 = orthogonal_complement_basis([outputs])
	basis2 = orthogonal_complement_basis(basis1[:-weight_cnt])
	good = [vec if min(vec) == 0 else -vec for vec in basis2 if min(vec) == 0 or max(vec) == 0]
	bad = [vec if min(vec) == 0 else -vec for vec in basis2 if min(vec) != 0 and max(vec) != 0]
	print(f"{len(good) = }, {len(bad) = }")
	for vec in bad:
		if not (-1 <= min(vec) and max(vec) <= 1):
			continue
		def update(delta):
			if min(vec + delta) == 0 and max(vec + delta) == 1:
				good.append(vec + delta)
				return True
			elif min(vec + delta) == -1 and max(vec + delta) == 0:
				good.append(-(vec + delta))
				return True
			return False
		found = False
		for use in [1, 2, 3]:
			for _vecs in itertools.product(good, repeat = use):
				for signs in itertools.product([1, -1], repeat = use):
					if update(sum(_vec * sign for _vec, sign in zip(_vecs, signs))):
						found = True
						break
				if found:
					break
			if found:
				break
		if not found:
			break
	if len(good) != weight_cnt:
		cnt[0] += 1
		print(f"FAIL1, {cnt = }")
		print()
		continue
	secret = 0
	for j in range(len(good[0])):
		s = 0
		for i in range(len(good)):
			s += good[i][j]
		if s not in [8, 9, 11, 12, 14, 15, 16, 17, 19, 20, 21]:
			break
		secret = secret << 1 | int(s in [8, 9])
	print(bin(secret)[2:].zfill(len(good[0])))
	flag = AES.new(hashlib.sha256(hex(secret).encode()).digest()[:16], AES.MODE_ECB).decrypt(enc_flag)
	print(flag)
	if flag.startswith(b"infobahn{"):
		cnt[1] += 1
		print(f"OK, {cnt = }")
		print()
	else:
		cnt[0] += 1
		print(f"FAIL2, {cnt = }")
		print()

"""
type     det triangle
T(1,2,2) 8   2
C(3,3)   9   2
T(1,2,3) 11  1
C(3,4)   12  1
T(2,2,2) 12  0
T(1,2,4) 14  1
T(1,3,3) 15  0
T(2,2,3) 16  0
T(1,2,5) 17  1
T(1,3,4) 19  0
T(2,2,4) 20  0
T(2,3,3) 21  0
"""
