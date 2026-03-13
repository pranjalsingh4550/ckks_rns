"""
TurboHE's CKKS implementation using RNS.
This file has CKKS. RNS is in rns.py.
Sympy (symbolic python) supports infinite precision integers, polynomials,
rings, moduli, etc.

With a `modulus` attribute, sympy also uses balanced ring representatives as in
TurboHE.
So, `modulus = 200` -> coefficients in [-100, +100).
"""

import sympy
from sympy import Poly
from sympy.abc import x
import os

verbose = False


try:
	n = int(os.getenv('DEGREE'))
except:
	n = 100

try:
	q = int(os.getenv('MODULUS'))
except:
	q = 200

if os.getenv('VERBOSE') == '1':
	verbose = True

mod_poly = Poly(x ** n + 1, x, modulus = q)

def failed():
	""" Perplexity-generated code. Does not run (let alone run correctly).
	"""
	mod2 = Poly(x ** 203 * 30405 + x + 601, x, domain = 'ZZ[200]')
	print(f"checking modulus: {mod2}\t{mod2 + 1}")
	mod2 = Poly(x ** 203 * 30405 + x + 601, x, domain = ZZ.map([200]))
	print(f"checking modulus: {mod2}\t{mod2 + 1}")

# Helpers
def print_list(l, depth = 0):
	for e in l:
		if isinstance(e, list):
			print_list(e, depth = depth + 1)
		else:
			ws = "\t" * depth
			print(f"{ws}{e}")
	print("\n")

def to_ciphertext(poln, mod = q):
	""" The plaintext space in TurboHE is Z[x]/(x^n + 1).
	The ciphertext space is the same modulo q.
	This does NOT encrypt @poln, just projects it to the ciphertext space.
	"""
	if verbose:
		print(f"# to_ciphertext: {mod}")

	as_sympy_poln = Poly(poln, modulus = mod)
	as_sympy_poln.degree() < n
	return as_sympy_poln

def make_random_poly(mod = q, deg = n, max_coeff = None):
	""" To generate small polynomials, use @mod = domain modulus, but change
	@max_coeff.
	"""
	if max_coeff is None:
		max_coeff = mod
	if verbose:
		print(f"# make_random_poly: q={mod} n={deg}")
	rnd = sympy.random_poly(x, deg - 1, 0, max_coeff - 1)
	return to_ciphertext(rnd, mod = mod)

def coeffs(poln):
	""" Highest first (Leading coefficient first)
	"""
	return Poly(poln).all_coeffs()

def poly_mult(p1, p2, mod = q, divisor_degree = n):
	""" Gentle reminder: all expressions are of degree `n - 1`, and the divisor
	is of degree `n`.
	Finds the remainder against the cyclotomic polynomial.
	"""
	assert isinstance(p1, Poly)
	assert isinstance(p2, Poly)
	assert p1.degree() == p2.degree()
	if verbose:
		print(f"# poly_mult: {divisor_degree}")

	mod = Poly(x ** divisor_degree + 1, x, modulus = mod)

	return (p1 * p2).rem(mod)

# Encryption helpers start here.

def get_encryption_key_dst(mod = q, deg = n):
	""" \\Chi_{enc}
	Values need not be small or large or something.
	Using uniform random polynomials.
	"""
	if verbose:
		print("# get_encryption_key_dst: {mod} {deg}")
	return make_random_poly(mod, deg)

def get_noise(mod = q, deg = n, max_coeff = 5):
	""" \\Chi_{err}.
	Might be incorrect.
	Returns small-coefficient polynomials.
	"""
	assert max_coeff.is_integer()
	return make_random_poly(mod = mod, deg = deg, max_coeff = 5)

def get_key(mod = q, deg = n):
	""" \\Chi_{key}.
	Returns random polynomials for now.
	"""
	return make_random_poly(mod, deg)

def setup_encryption(mod = q, deg = n):
	""" Returns sk and pk.
	Possible mistake: all operations here are already mod q.
	This is the KeyGen step in the TurboHE paper.
	"""
	if (verbose):
		print(f"# setup_encryption: {mod} {deg}")
	s = get_key(mod, deg)
	a = make_random_poly(mod, deg)
	err = get_noise(mod, deg)

	assert a.domain.mod == s.domain.mod
	assert err.domain.mod == a.domain.mod

	sk = (1, s)
	b = - poly_mult(a, s, mod = mod, divisor_degree = deg) + err
	pk = (b, a)

	return {'sk': sk, 'pk': pk}

def encrypt_plaintext(pt_poln, keys, mod = q, deg = n):
	""" Encrypts polynomials, not plaintext. Not at the moment.
	@pt_poln: plaintext polynomial
	DOUBT: is @pt_poln already mod @q? I have assumed yes.
	@keys: {'sk': XXX, 'pk': YYY}
	This samples errors e0, e1, which can be "forgotten" this point onwards.
	"""
	assert isinstance(keys, dict)
	assert 'sk' in keys
	assert 'pk' in keys
	assert isinstance(pt_poln, Poly)

	v = get_encryption_key_dst(mod = mod, deg = deg)
	e0 = get_noise(mod = mod, deg = deg)
	e1 = get_noise(mod = mod, deg = deg)

	""" Operation: ct = (c0, c1) = v.pk + (m + e0, e1) mod q
	"""
	ciphertext = (
		(poly_mult(v, keys['pk'][0], mod = mod, divisor_degree = deg) \
			+ pt_poln + e0),
		(poly_mult(v, keys['pk'][1], mod = mod, divisor_degree = deg) + e1)
	)

	return ciphertext

def decrypt_ciphertext(ciphertext, keys, mod = q, deg = n):
	""" ciphertext = (c0, c1).
	Operation: return m = < ct, sk > = (c0 + c1.secret_key) mod q
	"""
	assert isinstance(ciphertext, tuple)
	assert isinstance(ciphertext[0], Poly)
	assert isinstance(ciphertext[1], Poly)

	pt = ciphertext[0] + poly_mult(ciphertext[1], keys['sk'][1], mod = mod,
				divisor_degree = deg)
	return pt

def ciphertext_add(ct1, ct2, mod = n, deg = q):
	""" Doesn't use the degree.
	"""
	if verbose:
		print(f"ciphertext_add(): mod {mod}\n")

	assert isinstance(ct1[0], Poly)
	assert isinstance(ct2[1], Poly)
	assert len(ct1) == len(ct2) == 2
	assert ct1[0].domain.mod == ct2[0].domain.mod

	return (ct1[0] + ct2[0], ct1[1] + ct2[1])


def trial(mod, deg):
	""" Encrypt and decrypt a random polynomial.
	Returns (true_value + v.e_pk + e0 + sk.e1)
	e_pk from setup_encryption()
	e0, e1 from encrypt_plaintext()
	"""

	pt = make_random_poly(mod, deg)
	print(f"Made random polynomial plaintext {pt}")
	k = setup_encryption(mod, deg)
	print(f"keys: {k}")
	ct = encrypt_plaintext(pt, k, mod, deg)
	print(f"generated ciphertext (c0, c1):\n{ct[0]}\n{ct[1]}")
	decrypted = decrypt_ciphertext(ct, k, mod, deg)
	print(f"-----------------\nOriginal PT:\n{pt}\nDecrypyted pt:\n{decrypted}")

def trial_add(mod, deg):
	""" m1 and m2 use different encryption key values (v1, v2), but the same
	pk and sk.
	Error: same error term as trial(), for two terms.
	"""
	pt1 = make_random_poly(mod, deg)
	pt2 = make_random_poly(mod, deg)
	k = setup_encryption(mod, deg)
	print(f"\n\nADDITION\n{pt1}\n{pt2}\n{k}")
	ct1 = encrypt_plaintext(pt1, k, mod, deg)
	ct2 = encrypt_plaintext(pt2, k, mod, deg)

	ct = ciphertext_add(ct1, ct2)
	print(f"Completed addition")
	pt_out = decrypt_ciphertext(ct, k, mod, deg)
	print(f"decrypted output:\n{pt_out}")
	print(f"correct output:\n{pt1 + pt2}")


def main():
	print(f"Using n = {n}, q = {q}.\nModulus polynomial: {mod_poly}")
	trial(16384, 5)



if __name__ == "__main__":
	main()
